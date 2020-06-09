''' PCB板数据结构 '''


class Board:
    def __init__(self):
        self.serialNumber = ''  # 序列号
        self.jointBoard = False  # 是否拼板
        self.datetime = None  # 检查日期
        self.result = []  # 检查结果
        self.parts = []  # 元器件列表
        self.dirPath = '' # 程式路径
        self.cameraStatus = False # 相机状态


if  __name__ == '__main__':
    b1 = Board()
    b2 = Board()
    b1.serialNumber = 'abc'
    b1.result.append(199)
    print(b2)
    