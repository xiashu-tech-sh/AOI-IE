''' 程式定义文件。
    程式是人工制作的PCB板错漏反检测的基础数据，其实体是一个文件夹，该文件夹中包含了以下内容：
    1. image.jpg： 建立程式时候采集的原始图片
    2. template_1.jpg: 模板1的图片（若有）
    3. template_2.jpg: 模板2的图片（若有）
    4. mask_1.jpg: Mask图片（若有）
    5. mask_2.jpg: Mask图片（若有）
    6. info.json： 检测参数文件，包含PCB板ROI坐标、模板坐标、Mask坐标；
       及元器件序号、类别、坐标、检查项、阈值等信息
'''

import os
import json
import random
import cv2
from pprint import pprint
from collections import OrderedDict

from mask import Mask
from parts import Part, MISSING, MISMATCH, REVERSE
import algorithm as alg


class Pattern:
    def __init__(self, folder=''):
        ''' 创建程式，程式的基础信息包含在folder文件夹中 '''
        self.folder = folder
        self.imagefile = None  # 图片文件，位于目标文件夹下的image.jpg
        self.infofile = None  # 参数文件，位于目标文件夹下的info.jpg
        self.originCVImage = None  # 由相机采集的原始图像，未裁剪过的
        
        self.ax_pcbs = []  # PCB_ROI坐标集，格式 [x, y, w, h]
        self.ax_templates = []  # 模板坐标集，格式 [[x, y, w, h]]
        self.masks = []  # Mask坐标集，格式 [[x, y, w, h]], 注意：Mask坐标是相对于PCB_ROI的坐标
        self.parts = []

    def set_template(self, index, x, y, w, h):
        ''' 添加模板，或者修改模板。
            index：模板编号，取值[0,1]
        '''
        assert index in [0, 1]
        self.ax_templates[index] = [x, y, w, h]

    def set_mask(self, index, x, y, w, h):
        ''' 添加mask，或者修改mask。
            index：模板编号，取值[0, 1, 2, 3]
        '''
        assert index in [0, 1, 2, 3]
        self.masks[index] = [x, y, w, h]

    def set_pcb_coordinate(self, x, y, w, h):
        self.ax_pcbs = [x, y, w, h]

    def to_json(self):
        data = OrderedDict({
            'folder': self.folder,
            'ax_pcbs': self.ax_pcbs,
            'ax_templates': self.ax_templates,
            'masks': [],
            'parts': []})
        for mask in self.masks:
            data['masks'].append(mask.to_json())
        for part in self.parts:
            data['parts'].append(part.to_json())
        return data

    def save(self):
        if not self.folder or self.originCVImage is None:
            print('folder or image not found')
            return
        # save origin cv image
        imagefile = os.path.join(self.folder, 'image.jpg')
        cv2.imwrite(imagefile, self.originCVImage)
        # save parameter
        infofile = os.path.join(self.folder, 'info.json')
        with open(infofile, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, indent=2)

    def load(self, folder):
        ''' 从本地文件夹加载配置 '''
        assert os.path.exists(folder), '目标文件夹不存在'
        self.folder = folder
        imagefile = os.path.join(folder, 'image.jpg')
        assert os.path.exists(imagefile), '模板图片不存在'
        self.imagefile = imagefile
        infofile = os.path.join(folder, 'info.json')
        assert os.path.exists(infofile), '参数文件不存在'
        self.infofile = infofile

        # load image
        self.originCVImage = cv2.imread(imagefile)

        # clear first
        self.ax_pcbs.clear()
        self.masks.clear()
        self.ax_templates.clear()
        self.parts.clear()
        
        # load data
        with open(infofile, 'r', encoding='utf-8') as f:
            jsondata = json.load(f)
        
        self.ax_pcbs = list(jsondata['ax_pcbs'])
        self.ax_templates = list(jsondata['ax_templates'])
        for mask in jsondata['masks']:
            self.masks.append(Mask.from_json(mask))
        for part in jsondata['parts']:
            self.parts.append(Part.from_json(part))


    # @staticmethod
    # def from_json(jsondata):
    #     obj = Pattern(folder=jsondata['folder'])
    #     obj.ax_pcbs = list(jsondata['ax_pcbs'])
    #     obj.ax_templates = list(jsondata['ax_templates'])
    #     # obj.masks = list(jsondata['masks'])
    #     for mask in jsondata['masks']:
    #         obj.masks.append(Mask.from_json(mask))
    #     for part in jsondata['parts']:
    #         obj.parts.append(Part.from_json(part))
    #     return obj

    @staticmethod
    def from_folder(folder):
        ''' 从文件重建类 '''
        # filename = os.path.join(folder, 'info.json')
        # assert os.path.exists(filename), '文件不存在: {}'.format(filename)
        # with open(filename, 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        # return Pattern.from_json(data)
        obj = Pattern(folder=folder)
        obj.load(folder)
        return obj


''' 以下函数为测试用例 '''
def test_write_json(folder='./test_folder'):
    ''' 写入测试，随机生成数据后写入到指定文件 '''
    obj = Pattern(folder)
    algs = [alg.TemplateMatching(threshold=0.1), alg.GrayDiff(threshold=0.2), alg.AreaMatching(threshold=0.3), alg.BlobAnalyze(threshold=0.4)]
    for i in range(5):
        part = Part()
        part.x = 100 + i
        part.y = 100 + i
        part.w = 200 + i
        part.h = 200 + i

        key = random.choice([MISSING, MISMATCH, REVERSE])
        part.checkItems[key].extend(random.sample(algs, 2))

        obj.parts.append(part)
    
    with open('abc.json', 'w', encoding='utf-8') as f:
        json.dump(obj.to_json(), f, indent=2)

    return obj.to_json()


def test_restore_from_folder(folder='./test_folder'):
    ''' 根据json数据还原类 '''
    # with open('abc.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    return Pattern.from_folder(folder)


def test_invariance_between_write_and_read():
    ''' 测试写入json的数据和读取json的数据是否一致 '''
    jsonWrite = test_write_json()
    restoreObj = test_restore_from_folder()
    jsonRead = restoreObj.to_json()
    assert jsonWrite == jsonRead, '数据写入json前后不一致'


if __name__ == '__main__':
    test_invariance_between_write_and_read()
