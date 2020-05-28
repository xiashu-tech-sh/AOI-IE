''' 元器件类 '''
import algorithm as alg


class Part:
    def __init__(self):
        self.partNo = ''  # 料号
        self.classes = ''  # 元器件类别,如电阻、电容
        # 坐标，相对于Mask的坐标
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        # 检查项目
        self.checkItems = []

    def add_check_item(self, item):
        pass