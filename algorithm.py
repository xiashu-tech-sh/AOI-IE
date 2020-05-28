''' 算法 '''
import numpy as np


class TemplateMatching:
    def __init__(self, template=None):
        self.template = template

    def set_template(self, template):
        ''' 设定模板 '''
        assert isinstance(template, np.ndarray), 'template输入类型与np.ndarray不匹配'
        self.template = template.copy()

    def __call__(self, image, threshold=0.8, method=''):
        ''' 类调用，参数：
            image: 要比对的图片
            threshold：匹配度阈值，范围[0,1], 1为完全匹配
            method：模板匹配采用的方法 '''
        assert 0 <= threshold <= 1, '输入阈值threshold超出范围，范围0~1'
        # TODO:1.method参数给出选项，调研各个匹配方法的速度，准确度差异；2.匹配值转为0-1


class GrayDiff:
    ''' 灰度差算法 '''
    def __init__(self):
        pass


class EdgeMatching:
    ''' 边缘匹配算法 '''
    def __init__(self):
        pass


class BlobAnalyze:
    ''' Blob分析算法 '''
    def __init__(self):
        pass


class AreaMatching:
    ''' 区域匹配算法 '''
    def __init__(self):
        pass



if __name__ == '__main__':
    t = TemplateMatching()
    # t(1,1)
    img = np.random.randn(100,200)
    t.set_template(img)