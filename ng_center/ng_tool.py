#!/usr/bin/env python  
#coding=utf-8

import json
import random
from captcha.image import ImageCaptcha
import time

def make_result(res, data = None):
    result = {"res" : res, "systime" : int(time.time())}
    if data != None:
        result.update(data)
    return json.dumps(result)

image = ImageCaptcha(width=90, height=50, fonts=['font/arial.ttf'])
mcs = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
def make_captcha():
    s = ""
    for i in range(4):
        s = s + mcs[random.randint(0, len(mcs) - 1)]
    data = image.generate(s)
    return s, data

#data = make_captcha()
#from PIL import Image
#img = Image.open(data)
#img.show()
