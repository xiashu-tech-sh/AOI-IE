# flake8: noqa

from ._io import lblsave

from .image import apply_exif_orientation
from .image import img_arr_to_b64
from .image import img_b64_to_arr
from .image import img_data_to_arr
from .image import img_data_to_png_data

from .shape import labelme_shapes_to_label
from .shape import masks_to_bboxes
from .shape import polygons_to_mask
from .shape import shape_to_mask
from .shape import shapes_to_label

from .qt import newIcon
from .qt import newButton
from .qt import newAction
from .qt import addActions
from .qt import labelValidator
from .qt import struct
from .qt import distance
from .qt import distancetoline
from .qt import fmtShortcut


import cv2
import numpy as np

def cv_imread(filename):
    return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), cv2.IMREAD_COLOR)


def cv_imwrite(filename, image):
    param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
    cv2.imencode('.jpg', image, param)[1].tofile(filename)