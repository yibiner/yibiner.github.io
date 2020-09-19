#!/usr/bin/python

from PIL import Image
import os
from glob import glob
 
fpath = "./themes/matery/source/medias/banner"
# 定义要调整成为的尺寸（PIL会自动根据原始图片的长宽比来缩放适应设置的尺寸）
size = (1920, 1080)
# glob.glob()用来进行模糊查询，增加参数recursive=True后可以使用**/来匹配所有子目录
files = glob( fpath + "**/*.JPG", recursive=True) + glob(fpath + "**/*.jpg", recursive=True)
total = len(files) #总文件数
cur = 1 #当前文件序号
print("1920 开始处理 ", fpath)
print("-----------------------------------")
for infile in files:
    try:
        #f, ext = os.path.splitext(infile) # 分离文件名和后缀
        print("进度:" + str(cur) + "/" + str(total) + "   " + infile)
        img = Image.open(infile) # 打开图片文件
        if img.width > 2000:
            img.thumbnail(size, Image.ANTIALIAS) # 使用抗锯齿模式生成缩略图（压缩图片）
            img.save(infile, "JPEG") # 保存成与原文件名一致的文件，会自动覆盖源文件
        else:
            print(infile + "宽度小于2000px，无需处理，已忽略")
        cur = cur + 1
 
    except OSError:
        print(infile + "文件错误，忽略")

fpath = "./themes/matery/source/medias/featureimages"
# 定义要调整成为的尺寸（PIL会自动根据原始图片的长宽比来缩放适应设置的尺寸）
size = (1280, 800)
# glob.glob()用来进行模糊查询，增加参数recursive=True后可以使用**/来匹配所有子目录
files = glob( fpath + "**/*.JPG", recursive=True) + glob(fpath + "**/*.jpg", recursive=True)
total = len(files) #总文件数
cur = 1 #当前文件序号
print("1280 开始处理 ", fpath)
print("-----------------------------------")
for infile in files:
    try:
        #f, ext = os.path.splitext(infile) # 分离文件名和后缀
        print("进度:" + str(cur) + "/" + str(total) + "   " + infile)
        img = Image.open(infile) # 打开图片文件
        if img.width > 1280:
            img.thumbnail(size, Image.ANTIALIAS) # 使用抗锯齿模式生成缩略图（压缩图片）
            img.save(infile, "JPEG") # 保存成与原文件名一致的文件，会自动覆盖源文件
        else:
            print(infile + "宽度小于1280px，无需处理，已忽略")
        cur = cur + 1
 
    except OSError:
        print(infile + "文件错误，忽略")
