
from qtpy import QtCore
from qtpy import QtGui


# TODO(unknown):
# - [opt] Store paths instead of creating new ones at each paint.
from PyQt5.QtCore import Qt,QPointF

R, G, B = SHAPE_COLOR = 0, 255, 0  # green
DEFAULT_LINE_COLOR = QtGui.QColor(R, G, B, 128)                # bf hovering
DEFAULT_FILL_COLOR = QtGui.QColor(R, G, B, 128)                # hovering
DEFAULT_SELECT_LINE_COLOR = QtGui.QColor(255, 255, 255)        # selected
DEFAULT_SELECT_FILL_COLOR = QtGui.QColor(R, G, B, 155)         # selected
DEFAULT_VERTEX_FILL_COLOR = QtGui.QColor(R, G, B, 255)         # hovering
DEFAULT_HVERTEX_FILL_COLOR = QtGui.QColor(255, 255, 255, 255)  # hovering


class Shape(object):

    P_SQUARE, P_ROUND = 0, 1

    MOVE_VERTEX, NEAR_VERTEX = 0, 1

    # The following class variables influence the drawing of all shape objects.
    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    hvertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR
    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    def __init__(self, label=None, line_color=None, shape_type=None,
                 flags=None, group_id=None):
        self.label = label
        self.group_id = group_id
        self.points = []
        self.fill = False
        self.selected = False
        self.shape_type = shape_type
        self.flags = flags
        self.other_data = {}

        self._highlightIndex = None
        self._highlightMode = self.NEAR_VERTEX
        self._highlightSettings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }



        if line_color is not None:
            # Override the class line_color attribute
            # with an object attribute. Currently this
            # is used for drawing the pending line a different color.
            self.line_color = line_color

        self.shape_type = shape_type
    def getRectFromLine(self, pt1, pt2):
        x1, y1 = pt1.x(), pt1.y()
        x2, y2 = pt2.x(), pt2.y()
        return QtCore.QRectF(x1, y1, x2 - x1, y2 - y1)
    def addPoint(self, point):
        if self.points and point == self.points[0]:
            self.close()
        else:

            self.points.append(point)


    def paint(self, painter):
        if self.points:
            color = self.select_line_color \
                if self.selected else self.line_color
            pen = QtGui.QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            # pen.setStyle(Qt.DotLine)
            painter.setPen(pen)

            line_path = QtGui.QPainterPath()
            vrtx_path = QtGui.QPainterPath()


            assert len(self.points) in [1, 2]
            if len(self.points) == 2:
                rectangle = self.getRectFromLine(*self.points)
                line_path.addRect(rectangle)
            for i in range(len(self.points)):
                self.drawVertex(vrtx_path, i)


            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            # painter.fillPath(vrtx_path, self._vertex_fill_color)
            if self.fill:
                color = self.select_fill_color \
                    if self.selected else self.fill_color
                painter.fillPath(line_path, color)
    def drawVertex(self, path, i):
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.points[i]
        if i == self._highlightIndex:
            size, shape = self._highlightSettings[self._highlightMode]
            d *= size
        if self._highlightIndex is not None:
            self._vertex_fill_color = self.hvertex_fill_color
        else:
            self._vertex_fill_color = self.vertex_fill_color
        if shape == self.P_SQUARE:
            path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"

    def __len__(self):
        print("执行26")

        return len(self.points)

    def __getitem__(self, key):
        print("执行27")

        return self.points[key]
    def containsPoint(self, point):
        return self.makePath().contains(point)

    def makePath(self):

        path = QtGui.QPainterPath()
        if len(self.points) == 2:
            rectangle = self.getRectFromLine(*self.points)
            path.addRect(rectangle)

        return path

    def moveVertexBy(self, i, offset):
        self.points[i] = self.points[i] + offset