''' 算法 '''
import json
import numpy as np
from collections import OrderedDict


''' 算法异常 '''
class AlgorithmError(Exception):
    def __init__(self,  *args, **kwargs):
        super().__init__( *args, **kwargs)


class TemplateMatching:
    def __init__(self, template=None, threshold=0.8):
        ''' 模板匹配算法 '''
        self.template = template
        self.threshold = threshold

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
        self.threshold = threshold
        # TODO:1.method参数给出选项，调研各个匹配方法的速度，准确度差异；2.匹配值转为0-1

    def to_json(self):
        return OrderedDict({
            'algorithm': 'TemplateMatching',
            'threshold': self.threshold
        })

    @staticmethod
    def from_json(jsondata):
        return TemplateMatching(threshold=float(jsondata['threshold']))


class GrayDiff:
    def __init__(self, threshold=0.8):
        ''' 灰度差算法 '''
        self.threshold = threshold

    def to_json(self):
        return OrderedDict({
            'algorithm': 'GrayDiff',
            'threshold': self.threshold
        })

    @staticmethod
    def from_json(jsondata):
        return GrayDiff(threshold=float(jsondata['threshold']))


class EdgeMatching:
    ''' 边缘匹配算法 '''
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def to_json(self):
        return OrderedDict({
            'algorithm': 'EdgeMatching',
            'threshold': self.threshold
        })

    @staticmethod
    def from_json(jsondata):
        return EdgeMatching(threshold=float(jsondata['threshold']))


class BlobAnalyze:
    ''' Blob分析算法 '''
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def to_json(self):
        return OrderedDict({
            'algorithm': 'BlobAnalyze',
            'threshold': self.threshold
        })

    @staticmethod
    def from_json(jsondata):
        return BlobAnalyze(threshold=float(jsondata['threshold']))


class AreaMatching:
    ''' 区域匹配算法 '''
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def to_json(self):
        return OrderedDict({
            'algorithm': 'AreaMatching',
            'threshold': self.threshold
        })

    @staticmethod
    def from_json(jsondata):
        return AreaMatching(threshold=float(jsondata['threshold']))
    


# 通过名称索引类
nameToClass = {'TemplateMatching': TemplateMatching,
               'GrayDiff': GrayDiff,
               'EdgeMatching': EdgeMatching,
               'BlobAnalyze': BlobAnalyze,
               'AreaMatching': AreaMatching}


def restore_alg_item(jsondata):
    ''' 通过字典重建类 '''
    algName = jsondata.get('algorithm')
    if not algName or algName not in nameToClass.keys():
        raise AlgorithmError('restore algorithm item fail.')
    # 实例化对象
    obj = nameToClass[algName].from_json(jsondata)
    # 特殊参数处理
    if algName == 'TemplateMatching':
        pass
    elif algName == 'GrayDiff':
        pass
    elif algName == 'EdgeMatching':
        pass
    elif algName == 'BlobAnalyze':
        pass
    elif algName == 'AreaMatching':
        pass
    
    return obj


if __name__ == '__main__':
    t = TemplateMatching()
    img = np.random.randn(100,200)
    t.set_template(img)