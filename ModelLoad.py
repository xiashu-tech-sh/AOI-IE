import torch
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from PIL import Image
import cv2
import numpy as np
from collections import OrderedDict

import models.crnn as crnn
import dataset
import argparse
import craft_utils
import imgproc
import file_utils
from craft import CRAFT
import utils
from utils_model import strLabelConverter

class model_add():

    def __init__(self,cuda,model_path = './weights/netCRNN_24_120.pth'):
        self.alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
        self.model_path = model_path
        self.model = crnn.CRNN(32, 1, 37, 256)
        self.model = torch.nn.DataParallel(self.model)
        if torch.cuda.is_available():
            self.model = self.model.cuda()
        self.model.load_state_dict(torch.load(self.model_path, map_location='cpu'))
        self.converter = strLabelConverter(self.alphabet)
        self.transformer = dataset.resizeNormalize((100, 32))
        self.model.eval()
        print("cuda",cuda)
        self.parser = argparse.ArgumentParser(description='CRAFT Text Detection')
        self.parser.add_argument('--trained_model', default='weights/craft_mlt_25k.pth', type=str, help='pretrained model')
        self.parser.add_argument('--text_threshold', default=0.7, type=float, help='text confidence threshold')
        self.parser.add_argument('--low_text', default=0.4, type=float, help='text low-bound score')
        self.parser.add_argument('--link_threshold', default=0.4, type=float, help='link confidence threshold')
        self.parser.add_argument('--cuda', default=cuda, type=self.str2bool, help='Use cuda for inference')
        self.parser.add_argument('--canvas_size', default=1280, type=int, help='image size for inference')
        self.parser.add_argument('--mag_ratio', default=1.5, type=float, help='image magnification ratio')
        self.parser.add_argument('--poly', default=False, action='store_true', help='enable polygon type')
        self.parser.add_argument('--show_time', default=False, action='store_true', help='show processing time')
        self.parser.add_argument('--test_folder', default='/data/', type=str, help='folder path to input images')
        self.parser.add_argument('--refine', default=False, action='store_true', help='enable link refiner')
        self.parser.add_argument('--refiner_model', default='weights/craft_refiner_CTW1500.pth', type=str, help='pretrained refiner model')
        self.parser.add_argument('--image', default='./data/1.jpg', type=str, help='image to be tested')

        self.args = self.parser.parse_args()
        image_list, _, _ = file_utils.get_files(self.args.test_folder)
        self.net = CRAFT()
        if self.args.cuda:
            self.net.load_state_dict(self.copyStateDict(torch.load(self.args.trained_model)))
        else:
            self.net.load_state_dict(self.copyStateDict(torch.load(self.args.trained_model, map_location='cpu')))
        if self.args.cuda:
            self.net = self.net.cuda()
            self.net = torch.nn.DataParallel(self.net)
            cudnn.benchmark = False
        self.refine_net = None
        self.net.eval()
        if self.args.refine:
            from refinenet import RefineNet
            self.refine_net = RefineNet()
            if self.args.cuda:
                self.refine_net.load_state_dict(self.copyStateDict(torch.load(self.args.refiner_model)))
                refine_net = self.refine_net.cuda()
                refine_net = torch.nn.DataParallel(refine_net)
            else:
                self.refine_net.load_state_dict(self.copyStateDict(torch.load(self.args.refiner_model, map_location='cpu')))
                self.refine_net.eval()
            self.args.poly = True
    def segmentation(self,image_numpy):
        bboxes, polys, score_text = self.test_net(self.net, image_numpy, self.args.text_threshold, self.args.link_threshold, self.args.low_text,
                                             self.args.cuda, self.args.poly,self.refine_net)
        result = ''
        crop = 0
        for bbox in bboxes:
            x1 = int(bbox[0][0])
            x2 = int(bbox[2][0])
            y1 = int(bbox[0][1])
            y2 = int(bbox[2][1])
            crop_image = image_numpy[y1:y2, x1:x2]
            cv2.imwrite("%s.jpg"%crop,crop_image)
            crop+=1
            sim_pred = self.identify(crop_image)
            result+=sim_pred
        return result

    def identify(self,image_num):
        image_pil =  Image.fromarray(cv2.cvtColor(image_num,cv2.COLOR_BGR2RGB)).convert('L')
        image = self.transformer(image_pil)
        if torch.cuda.is_available():
            image = image.cuda()
        image = image.view(1, *image.size())
        # image = Variable(image)
        preds = self.model(image)

        _, preds = preds.max(2)
        preds = preds.transpose(1, 0).contiguous().view(-1)

        preds_size = Variable(torch.IntTensor([preds.size(0)]))
        sim_pred = self.converter.decode(preds.data, preds_size.data, raw=False)
        return sim_pred

    def copyStateDict(self,state_dict):
        if list(state_dict.keys())[0].startswith("module"):
            start_idx = 1
        else:
            start_idx = 0
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = ".".join(k.split(".")[start_idx:])
            new_state_dict[name] = v
        return new_state_dict

    def test_net(self,net, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net=None):
        # resize
        img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(image, self.args.canvas_size,
                                                                              interpolation=cv2.INTER_LINEAR,
                                                                              mag_ratio=self.args.mag_ratio)
        ratio_h = ratio_w = 1 / target_ratio

        # preprocessing
        x = imgproc.normalizeMeanVariance(img_resized)
        x = torch.from_numpy(x).permute(2, 0, 1)  # [h, w, c] to [c, h, w]
        x = Variable(x.unsqueeze(0))  # [c, h, w] to [b, c, h, w]
        if cuda:
            x = x.cuda()

        # forward pass
        with torch.no_grad():
            y, feature = net(x)

        # make score and link map
        score_text = y[0, :, :, 0].cpu().data.numpy()
        score_link = y[0, :, :, 1].cpu().data.numpy()

        # refine link
        if refine_net is not None:
            with torch.no_grad():
                y_refiner = refine_net(y, feature)
            score_link = y_refiner[0, :, :, 0].cpu().data.numpy()
        # Post-processing
        boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)
        boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
        polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
        for k in range(len(polys)):
            if polys[k] is None: polys[k] = boxes[k]
        # render results (optional)
        render_img = score_text.copy()
        render_img = np.hstack((render_img, score_link))
        ret_score_text = imgproc.cvt2HeatmapImg(render_img)

        return boxes, polys, ret_score_text

    def str2bool(v):
        return v.lower() in ("yes", "y", "true", "t", "1")
