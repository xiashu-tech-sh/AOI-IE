from PyQt5.QtCore import Qt, QLineF, QPointF, QPoint
from PyQt5.QtGui import QBrush, QPainter
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy import QT_VERSION

QT5 = QT_VERSION[0] == '5'
from shape import Shape
import utils

# TODO(unknown):
# - [maybe] Find optimal epsilon value.


CURSOR_DEFAULT = QtCore.Qt.ArrowCursor
CURSOR_POINT = QtCore.Qt.PointingHandCursor
CURSOR_DRAW = QtCore.Qt.CrossCursor
CURSOR_MOVE = QtCore.Qt.ClosedHandCursor
CURSOR_GRAB = QtCore.Qt.OpenHandCursor
import logging

logger = logging.getLogger('main.mod.submod')
logger.debug('绘图界面')

class Canvas(QtWidgets.QWidget):
    zoomRequest = QtCore.Signal(int, QtCore.QPoint)  # 缩放事件，按住ctrl+鼠标滚轮后触发
    scrollRequest = QtCore.Signal(int, int)  # 滚轮直接滚动：上下sroll； 按住alt+滚轮：左右scroll
    newShape = QtCore.Signal(str, str)  # 一个形状绘制完成后触发
    deleteShape = QtCore.Signal(str, str)  # 删除形状,参数：classes, name
    selectionChanged = QtCore.Signal(list)  # EDIT阶段，鼠标选中的Shape发生变化后触发，CREATE阶段不触发
    shapeMoved = QtCore.Signal(str, str)  # shape被拖动或者shape的角点被拖动后，左键释放后触发
    # drawingPolygon = QtCore.Signal(bool)
    # edgeSelected = QtCore.Signal(bool, object)
    # vertexSelected = QtCore.Signal(bool)
    testSelected = QtCore.Signal(list)  # 文本信号
    pasteShape = QtCore.Signal(str, str, list)
    CREATE, EDIT, VIEW = 0, 1, 2

    # polygon, rectangle, line, or point
    _shape_type = 'location'

    _fill_drawing = False

    def __init__(self, *args, **kwargs):
        self.epsilon = kwargs.pop('epsilon', 10.0)
        self.double_click = kwargs.pop('double_click', 'close')
        if self.double_click not in [None, 'close']:
            raise ValueError(
                'Unexpected value for double_click event: {}'
                    .format(self.double_click)
            )
        super(Canvas, self).__init__(*args, **kwargs)
        # Initialise local state.
        self.mode = self.EDIT  # EDIT:编辑模式，可以改变形状、移动、复制； CREATE:绘制模式
        self.shapes = []  # objects of Shape in shape.py
        self.shapesBackups = []  # 保存形状列表，如 [[shape1, shape2], [shape1, shape2, shape3]]
        self.current = None  # 当前形状，Shape类的实例对象
        self.selectedShapes = []  # save the selected shapes here

        self.line = Shape(shape_type='location')
        self.prevPoint = QtCore.QPoint()
        # self.prevMovePoint = QtCore.QPoint()
        self.offsets = QtCore.QPoint(), QtCore.QPoint()
        self.scale = 1.0  # 缩放因子，在pattern_widget.py文件中控制
        self.pixmap = None  # 背景图片
        # self.visible = {}
        self._hideBackround = False
        self.hideBackround = False
        self.hShape = None  # highlight shape
        # self.prevhShape = None
        self.hVertex = None  # highlight vertext
        # self.prevhVertex = None
        self.hEdge = None  # highlight edge
        # self.prevhEdge = None
        self.movingShape = False  # 正在移动图形标志，有两种形式：1. 鼠标左键按下拖动顶点； 2. 鼠标左键按下拖动图形
        self._painter = QtGui.QPainter()
        self._cursor = CURSOR_DEFAULT
        # Menus:
        # 0: right-click without selection and dragging of shapes
        # 1: right-click with selection and dragging of shapes
        self.menus = None

        # Set widget options.
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        # 存储的numpy格式的图像数据
        self.cvImage = None

        # 若为元器件，需标明当前元器件类型: 'capacitor', 'resistor', 'slot', 'component'
        self.part_type = ''
        # 正极指向负极线段坐标
        self.arrow_start = None
        self.arrow_end = None
        # 数据保存
        self.zoomInAction = False  # 放大
        self.zoomOutAction = False  # 缩小
        # 移动
        self._endPos = None
        self._startPos = None
        self._point = QPoint(0, 0)
        self.mobile = False
        self.left_click = False
        # 粘贴
        self.paste_pop = None
        # 复制中心点
        self.copy_center_pos = []
        # 复制
        self._copy = None
        self.copy_shape = None
        self.colox = []
    def delete_shape_action_clicked(self):
        if not self.hShape and not self.selectedShapes:
            return
        shape = self.selectedShapes.pop()
        self.deleteShape.emit(shape.shape_type, shape.name)
        self.shapes.remove(shape)
        name_index = 0
        for Nsha in self.shapes:
            if shape.shape_type == Nsha.shape_type:
                name_index += 1
                Nsha.name = '%s_%s' % (shape.shape_type, name_index)

    def paste_shape_action_clicke(self):
        if self.copy_shape:
            # shape = self.selectedShapes.pop()
            self.pasteShape.emit(self.copy_shape.shape_type, self.copy_shape.name, self.copy_center_pos)
            self.update()

    def copy_shape_action_clicke(self):
        if self._shape is None:
            return

        self.copy_shape = self._shape

    def fillDrawing(self):
        return self._fill_drawing

    def setFillDrawing(self, value):
        self._fill_drawing = value

    @property
    def shape_type(self):
        return self._shape_type

    @shape_type.setter
    def shape_type(self, value):
        if value not in ['location', 'template', 'mask', 'part', 'pos_neg']:
            raise ValueError('Unsupported shape_type: %s' % value)
        self._shape_type = value

    def enterEvent(self, ev):
        self.overrideCursor(self._cursor)

    def leaveEvent(self, ev):
        self.unHighlight()
        self.restoreCursor()

    def focusOutEvent(self, ev):
        self.restoreCursor()

    def isVisible(self, shape):
        return True

    def drawing(self):
        ''' 绘制模式 '''
        return self.mode == self.CREATE

    def editing(self):
        ''' 编辑模式 '''
        return self.mode == self.EDIT

    def setEditing(self, value=True):
        ''' 模式切换， True设置为编辑模式， False设置为绘制模式 '''
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.unHighlight()
            self.deSelectShape()

    def unHighlight(self):
        if self.hShape:
            self.hShape.highlightClear()
            self.update()
        self.hShape = self.hVertex = self.hEdge = None

    def selectedVertex(self):
        ''' 选中的顶点 '''
        return self.hVertex is not None

    def mouseMoveEvent(self, ev):
        # 鼠标移动事件
        """Update line with last point and current coordinates."""
        try:
            if QT5:
                pos = self.transformPos(ev.localPos())
            else:
                pos = self.transformPos(ev.posF())
        except AttributeError:
            return

        self.restoreCursor()
        if self.mobile:
            self.overrideCursor(CURSOR_GRAB)
            if self.left_click:
                self.overrideCursor(CURSOR_MOVE)
                self._endPos = pos - self._startPos
                self._point = self._point + self._endPos
                self._startPos = pos
                self.repaint()
        # Polygon drawing.
        if self.drawing():
            self.line.shape_type = self.shape_type

            self.overrideCursor(CURSOR_DRAW)
            if not self.current:
                return

            if self.outOfPixmap(pos):
                # Don't allow the user to draw outside the pixmap.
                # Project the point to the pixmap's edges.
                pos = self.intersectionPoint(self.current[-1], pos)

            # zp add, 只绘制矩形
            self.line.points = [self.current[0], pos]
            # self.line.close()

            self.repaint()
            self.current.highlightClear()
            return

        # Polygon/Vertex moving. the left button is pressed
        if QtCore.Qt.LeftButton & ev.buttons():
            if self.shape_type == "pos_neg" :
                if len(self.shapes) == 2 :
                    if   self.shapes[1][0].x() - self.shapes[0][1].x() <= 5:
                        self.arrow_start = QPointF(
                            (self.shapes[0][1].x() - self.shapes[0][0].x()) // 2 + self.shapes[0][0].x(),
                            self.shapes[0][1].y())
                        self.arrow_end = QPointF(
                            (self.shapes[1][1].x() - self.shapes[1][0].x()) // 2 + self.shapes[1][0].x(),
                            self.shapes[1][0].y() - 5, )
                    else:
                        self.arrow_start = QPointF(self.shapes[0][1].x(),
                                                   (self.shapes[0][1].y() - self.shapes[0][0].y()) // 2 + self.shapes[0][
                                                       0].y())
                        self.arrow_end = QPointF(self.shapes[1][0].x() - 5,
                                                 (self.shapes[1][1].y() - self.shapes[1][0].y()) // 2 + self.shapes[1][
                                                     0].y())
                if self.hShape:
                    self.testSelected.emit(self.hShape.points)
            if self.selectedVertex():
                if self.hShape.shape_type != self.shape_type:
                    return
                self.boundedMoveVertex(pos)
                self.repaint()
                self.movingShape = True
            # 选中矩形
            elif self.selectedShapes and self.prevPoint:
                if self.hShape is None or self.hShape.shape_type != self.shape_type:
                    return
                self.overrideCursor(CURSOR_MOVE)
                self.boundedMoveShapes(self.selectedShapes, pos)
                self.repaint()
                self.movingShape = True

            return

        # Just hovering over the canvas, 2 possibilities:
        # - Highlight shapes
        # - Highlight vertex
        # Update shape/vertex fill and tooltip value accordingly.
        # self.setToolTip(self.tr("Image"))
        for shape in reversed([s for s in self.shapes if self.isVisible(s)]):
            if shape.shape_type != self.shape_type:
                continue
            # Look for a nearby vertex to highlight. If that fails,
            # check if we happen to be inside a shape.
            index = shape.nearestVertex(pos, self.epsilon / self.scale)
            index_edge = shape.nearestEdge(pos, self.epsilon / self.scale)
            if index is not None:
                if self.selectedVertex():
                    self.hShape.highlightClear()
                self.hVertex = index
                self.hShape = shape
                self._shape = shape
                self.hEdge = index_edge
                shape.highlightVertex(index, shape.MOVE_VERTEX)
                self.overrideCursor(CURSOR_POINT)
                self.setToolTip(self.tr("Click & drag to move point"))
                self.setStatusTip(self.toolTip())
                self.update()
                break
            elif shape.containsPoint(pos):
                if self.selectedVertex():
                    self.hShape.highlightClear()
                self.hVertex = None
                self.hShape = shape
                self._shape = shape
                self.hEdge = index_edge
                self.setToolTip(
                    self.tr("Click & drag to move shape '%s'") % shape.name)
                self.setStatusTip(self.toolTip())
                self.overrideCursor(CURSOR_GRAB)
                self.update()
                break
            else:  # Nothing found, clear highlights, reset state.
                self._shape = None
                self.unHighlight()
                # self.edgeSelected.emit(self.hEdge is not None, self.hShape)
                # self.vertexSelected.emit(self.hVertex is not None)

    def mousePressEvent(self, ev):

        if self.zoomOutAction:
            if self.scale <= 0.2:
                # TODO
                return
            self.scale -= 0.1
            self.update()
            return
        elif self.zoomInAction:

            self.scale += 0.1
            self.update()
            return
        # 鼠标点击事件
        logger.debug('开始绘制，当前绘制类型：%s'% self.part_type)
        if not self.pixmap:
            return
        if QT5:
            pos = self.transformPos(ev.localPos())
        else:
            pos = self.transformPos(ev.posF())
        if ev.button() == QtCore.Qt.LeftButton:
            if self.mobile:
                self.left_click = True
                self.overrideCursor(CURSOR_MOVE)
                self._startPos = pos
                return
            if self.drawing():
                if self.current:
                    # zp add, 只绘制矩形
                    assert len(self.current.points) == 1
                    self.current.points = self.line.points
                    self.finalise()  # 把 current拷贝到相应列表，完成绘制
                    logger.debug('%s, 绘制完成'%self.part_type)
                elif not self.outOfPixmap(pos):
                    # Mask只允许有4个，Location只允许有三个
                    # Create new shape.
                    self.current = Shape(shape_type=self.shape_type, part_type=self.part_type)
                    self.current.addPoint(pos)

                    self.line.points = [pos, pos]
                    self.setHiding()
                    # self.drawingPolygon.emit(True)
                    self.update()

            else:
                group_mode = (int(ev.modifiers()) == QtCore.Qt.ControlModifier)
                self.selectShapePoint(pos, multiple_selection_mode=group_mode)
                self.prevPoint = pos
                self.repaint()
        elif ev.button() == QtCore.Qt.RightButton and self.editing():
            group_mode = (int(ev.modifiers()) == QtCore.Qt.ControlModifier)
            self.selectShapePoint(pos, multiple_selection_mode=group_mode)
            self.prevPoint = pos
            self.repaint()

    def resizeEvent(self, e):
        if self.mobile:
            if self.parent is not None:
                self.scaled_img = self.img.scaled(self.size())
                self.point = QPoint(0, 0)
                self.update()

    def mouseReleaseEvent(self, ev):
        # 鼠标释放
        if ev.button() == QtCore.Qt.RightButton:
            pos = self.transformPos(ev.localPos())
            self.copy_center_pos = [pos.x(), pos.y()]
            try:
                self.menus[1].exec_(self.mapToGlobal(ev.pos()))
            except:
                pass
            self.repaint()
            # menu = self.menus[len(self.selectedShapesCopy) > 0]
            # self.restoreCursor()
            # if not menu.exec_(self.mapToGlobal(ev.pos())) \
            #         and self.selectedShapesCopy:
            #     # Cancel the move by deleting the shadow copy.
            #     self.selectedShapesCopy = []
            #     self.repaint()
        elif ev.button() == QtCore.Qt.LeftButton:
            if self.mobile:
                self.left_click = False
                return
            if self.selectedShapes:
                if self.hShape is None or self.hShape.shape_type != self.shape_type:
                    return
            self.overrideCursor(CURSOR_GRAB)
        if self.movingShape and self.hShape:
            index = self.shapes.index(self.hShape)
            # if (self.shapesBackups[-1][index].points !=
            #         self.shapes[index].points):
            #     self.storeShapes()
            #     self.shapeMoved.emit()

            self.movingShape = False
            self.shapeMoved.emit(self.hShape.shape_type, self.hShape.name)

    def setHiding(self, enable=True):
        self._hideBackround = self.hideBackround if enable else False

    def canCloseShape(self):
        return self.drawing() and self.current and len(self.current) > 2

    def selectShapePoint(self, point, multiple_selection_mode):
        """Select the first shape created which contains this point."""

        if self.hShape is None or self.hShape.shape_type != self.shape_type:
            return
        if self.selectedVertex():  # A vertex is marked for selection.
            index, shape = self.hVertex, self.hShape
            shape.highlightVertex(index, shape.MOVE_VERTEX)

            self.selectionChanged.emit([shape])
        else:
            for shape in reversed(self.shapes):
                if shape.shape_type != self.shape_type:
                    continue
                if self.isVisible(shape) and shape.containsPoint(point):
                    self.calculateOffsets(shape, point)
                    self.setHiding()
                    if multiple_selection_mode:
                        if shape not in self.selectedShapes:
                            self.selectionChanged.emit(
                                self.selectedShapes + [shape])
                    else:
                        self.selectionChanged.emit([shape])
                    return
        self.deSelectShape()

    def calculateOffsets(self, shape, point):
        rect = shape.boundingRect()
        x1 = rect.x() - point.x()
        y1 = rect.y() - point.y()
        x2 = (rect.x() + rect.width() - 1) - point.x()
        y2 = (rect.y() + rect.height() - 1) - point.y()
        self.offsets = QtCore.QPoint(x1, y1), QtCore.QPoint(x2, y2)

    def boundedMoveVertex(self, pos):
        index, shape = self.hVertex, self.hShape
        point = shape[index]
        if self.outOfPixmap(pos):
            pos = self.intersectionPoint(point, pos)
        shape.moveVertexBy(index, pos - point)

    def boundedMoveShapes(self, shapes, pos):
        if self.outOfPixmap(pos):
            return False  # No need to move
        o1 = pos + self.offsets[0]
        if self.outOfPixmap(o1):
            pos -= QtCore.QPoint(min(0, o1.x()), min(0, o1.y()))
        o2 = pos + self.offsets[1]
        if self.outOfPixmap(o2):
            pos += QtCore.QPoint(min(0, self.pixmap.width() - o2.x()),
                                 min(0, self.pixmap.height() - o2.y()))
        # XXX: The next line tracks the new position of the cursor
        # relative to the shape, but also results in making it
        # a bit "shaky" when nearing the border and allows it to
        # go outside of the shape's area for some reason.
        # self.calculateOffsets(self.selectedShapes, pos)
        dp = pos - self.prevPoint
        if dp:
            for shape in shapes:
                shape.moveBy(dp)
            self.prevPoint = pos
            return True
        return False

    def deSelectShape(self):
        if self.selectedShapes:
            self.setHiding(False)
            self.selectionChanged.emit([])
            self.update()

    def boundedShiftShapes(self, shapes):
        # Try to move in one direction, and if it fails in another.
        # Give up if both fail.
        point = shapes[0][0]
        offset = QtCore.QPoint(2.0, 2.0)
        self.offsets = QtCore.QPoint(), QtCore.QPoint()
        self.prevPoint = point
        if not self.boundedMoveShapes(shapes, point - offset):
            self.boundedMoveShapes(shapes, point + offset)

    def paintEvent(self, event):
        if not self.pixmap:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())
        # self.draw_img(p)
        # p.drawPixmap(0, 0, self.pixmap)
        p.drawPixmap(self._point, self.pixmap)
        Shape.scale = self.scale
        for shape in self.shapes:
            # 此处只显示当前种类的方框，根据TabWidget界面选择情况进行切换，比如Mask页面只显示Mask框
            # shape.paint(p)
            if shape.shape_type != self.shape_type:
                continue
            if (shape.selected or not self._hideBackround) and \
                    self.isVisible(shape):
                shape.fill = shape.selected or shape == self.hShape
                shape.paint(p)
        if self.current:
            pen = QtGui.QPen()
            self.current.paint(p)
            self.line.paint(p)

        # 绘制箭头
        # if self.shape_type == 'pos_neg' :
        #     pen = QtGui.QPen(Qt.yellow,4)
        #     p.setPen(pen)
        #     brush = QBrush()
        #     brush.setColor(Qt.yellow)
        #     p.drawRect(self.colox[0],self.colox[1],self.colox[2],self.colox[3])


        p.end()

    def draw_img(self, painter):
        painter.drawPixmap(self._point, self.scaled_img)

    def transformPos(self, point):
        """Convert from widget-logical coordinates to painter-logical ones."""
        return point / self.scale - self.offsetToCenter()

    def offsetToCenter(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QtCore.QPoint(x, y)

    def outOfPixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w - 1 and 0 <= p.y() <= h - 1)

    def finalise(self):
        assert self.current
        self.shapes.append(self.current)
        self.current = None
        self.setHiding(False)
        self.newShape.emit(self.shape_type, self.part_type)
        self.update()

    def closeEnough(self, p1, p2):
        # d = distance(p1 - p2)
        # m = (p1-p2).manhattanLength()
        # print "d %.2f, m %d, %.2f" % (d, m, d - m)
        # divide by scale to allow more precision when zoomed in
        return utils.distance(p1 - p2) < (self.epsilon / self.scale)

    def intersectionPoint(self, p1, p2):
        # Cycle through each image edge in clockwise fashion,
        # and find the one intersecting the current line segment.
        # http://paulbourke.net/geometry/lineline2d/
        size = self.pixmap.size()
        points = [(0, 0),
                  (size.width() - 1, 0),
                  (size.width() - 1, size.height() - 1),
                  (0, size.height() - 1)]
        # x1, y1 should be in the pixmap, x2, y2 should be out of the pixmap
        x1 = min(max(p1.x(), 0), size.width() - 1)
        y1 = min(max(p1.y(), 0), size.height() - 1)
        x2, y2 = p2.x(), p2.y()
        d, i, (x, y) = min(self.intersectingEdges((x1, y1), (x2, y2), points))
        x3, y3 = points[i]
        x4, y4 = points[(i + 1) % 4]
        if (x, y) == (x1, y1):
            # Handle cases where previous point is on one of the edges.
            if x3 == x4:
                return QtCore.QPoint(x3, min(max(0, y2), max(y3, y4)))
            else:  # y3 == y4
                return QtCore.QPoint(min(max(0, x2), max(x3, x4)), y3)
        return QtCore.QPoint(x, y)

    def intersectingEdges(self, point1, point2, points):
        """Find intersecting edges.

        For each edge formed by `points', yield the intersection
        with the line segment `(x1,y1) - (x2,y2)`, if it exists.
        Also return the distance of `(x2,y2)' to the middle of the
        edge along with its index, so that the one closest can be chosen.
        """
        (x1, y1) = point1
        (x2, y2) = point2
        for i in range(4):
            x3, y3 = points[i]
            x4, y4 = points[(i + 1) % 4]
            denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            nua = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
            nub = (x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)
            if denom == 0:
                # This covers two cases:
                #   nua == nub == 0: Coincident
                #   otherwise: Parallel
                continue
            ua, ub = nua / denom, nub / denom
            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                m = QtCore.QPoint((x3 + x4) / 2, (y3 + y4) / 2)
                d = utils.distance(m - QtCore.QPoint(x2, y2))
                yield d, i, (x, y)

    # These two, along with a call to adjustSize are required for the
    # scroll area.
    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    def wheelEvent(self, ev):
        if QT5:
            mods = ev.modifiers()
            delta = ev.angleDelta()
            if QtCore.Qt.ControlModifier == int(mods):
                # with Ctrl/Command key
                # zoom
                self.zoomRequest.emit(delta.y(), ev.pos())
            else:
                # scroll
                self.scrollRequest.emit(delta.x(), QtCore.Qt.Horizontal)
                self.scrollRequest.emit(delta.y(), QtCore.Qt.Vertical)
        else:
            if ev.orientation() == QtCore.Qt.Vertical:
                mods = ev.modifiers()
                if QtCore.Qt.ControlModifier == int(mods):
                    # with Ctrl/Command key
                    self.zoomRequest.emit(ev.delta(), ev.pos())
                else:
                    self.scrollRequest.emit(
                        ev.delta(),
                        QtCore.Qt.Horizontal
                        if (QtCore.Qt.ShiftModifier == int(mods))
                        else QtCore.Qt.Vertical)
            else:
                self.scrollRequest.emit(ev.delta(), QtCore.Qt.Horizontal)
        ev.accept()

    # def keyPressEvent(self, ev):
    #     key = ev.key()
    #     if key == QtCore.Qt.Key_Escape and self.current:
    #         self.current = None
    #         self.drawingPolygon.emit(False)
    #         self.update()
    #     elif key == QtCore.Qt.Key_Return and self.canCloseShape():
    #         self.finalise()

    def loadPixmap(self, pixmap):
        self.pixmap = pixmap
        # 清空所有形状
        self.shapes.clear()
        self.repaint()

    def loadShapes(self, shapes, replace=True):
        if replace:
            self.shapes = list(shapes)
        else:
            self.shapes.extend(shapes)
        self.current = None
        self.hShape = None
        self.hVertex = None
        self.hEdge = None
        self.repaint()

    def overrideCursor(self, cursor):
        ''' 改变光标形状，比如绘制的时候变为十字形，编辑的时候变为箭头形状 '''
        self.restoreCursor()
        self._cursor = cursor
        QtWidgets.QApplication.setOverrideCursor(cursor)

    def restoreCursor(self):
        ''' 恢复光标形状 '''
        QtWidgets.QApplication.restoreOverrideCursor()

    def resetState(self):
        ''' 重置，pixmap设为None '''
        self.restoreCursor()
        self.pixmap = None
        # self.shapesBackups = []
        self.update()
