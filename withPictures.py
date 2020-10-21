# !/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import argparse
import os

from glob import glob
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def waterMark(path, fontFileName='OPPOSans-L.ttf'):
    if not os.path.isfile(fontFileName):
        print("缺少字体文件", fontFileName)
        return

    # if path == 'all':
    #     path = '*'
    # dir_name = path + '/*'
    files = glob( path + "**/*.JPG", recursive=True) + glob(path + "**/*.jpg", recursive=True)
    # files = glob(dir_name)
    for fileName in files:
        im = Image.open(fileName)
        if len(im.getbands()) < 3:
            im = im.convert('RGB')
            print(fileName)
        font = ImageFont.truetype(fontFileName, max(30, int(im.size[1] / 20)))
        draw = ImageDraw.Draw(im)
        # 在图片中心添加水印 fill:RGB 颜色值
        draw.text((im.size[0] / 2, im.size[1] / 2),
                  u'@Yibin', fill=(47,79,79), font=font)
        im.save(fileName)

def zipPic(fpath, x=1920, y=1080):
    # 定义要调整成为的尺寸（PIL会自动根据原始图片的长宽比来缩放适应设置的尺寸）
    size = (x, y)
    # glob.glob()用来进行模糊查询，增加参数recursive=True后可以使用**/来匹配所有子目录
    files = glob( fpath + "**/*.JPG", recursive=True) + glob(fpath + "**/*.jpg", recursive=True)
    total = len(files) #总文件数
    cur = 1 #当前文件序号
    print("x:{} y:{} 开始处理 路径:{}".format(x, y, fpath))
    print("-----------------------------------")
    for infile in files:
        try:
            #f, ext = os.path.splitext(infile) # 分离文件名和后缀
            
            img = Image.open(infile) # 打开图片文件
            if img.width > x:
                img.thumbnail(size, Image.ANTIALIAS) # 使用抗锯齿模式生成缩略图（压缩图片）
                img.save(infile, "JPEG") # 保存成与原文件名一致的文件，会自动覆盖源文件
                print("进度:" + str(cur) + "/" + str(total) + "   " + infile)
            else:
                print("进度:" + str(cur) + "/" + str(total) + "   " + infile + "   忽略")
            cur = cur + 1
    
        except OSError:
            print(infile + " 文件错误，忽略")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help="需要处理的图片路径")
    parser.add_argument('-x', '--x', type=int, default=1920, help="压缩图片设置横向像素，默认1920")
    parser.add_argument('-y', '--y', type=int, default=1080, help="压缩图片设置纵向像素，默认1080")
    parser.add_argument('-z', '--zip', action='store_true', help='压缩图片，减小图片大小')
    parser.add_argument('-w', '--water', action='store_true', help='添加水印，依赖STSONG.TTF字库')

    args = parser.parse_args()

    if args.path is None or args.path == "":
        print("当前路径为", os.getcwd())
        path = os.getcwd()
    else:
        path = args.path


    if args.zip:
        zipPic(path, args.x, args.y)
    if args.water:
        waterMark(path)
