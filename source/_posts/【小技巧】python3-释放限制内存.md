---
title: 【小技巧】python3 释放、限制内存
top: false
cover: false
toc: true
mathjax: true
date: 2020-09-16 19:42:13
password:
summary: 使用Python脚本自动拉取日志并提取有用字段数据时，会因为需要统计数据的日志文件过多，导致运行时候脚本占用过多内存
tags:
- Python
- 内存
categories:
- 小技巧
---

## 前言

使用Python脚本自动拉取日志并提取有用字段数据时，会因为需要统计数据的日志文件过多，导致运行时候脚本占用过多内存。

比如日志文件是每小时进行一次归档，单个日志文件1GB，需要获取一天内的日志统计信息，那将会有24GB日志信息，如果在8GB内存机器上分析，同时还有其他任务在运行，最好能直接限制单个脚本的内存占用。





## 释放、限制内存

释放内存： 读取分析完单个文件后，在读取分析下个文件前及时del

```python
for filename in files:
        with open(filename, "r") as f:
            lines = f.readlines()
        tmpdata = dealwithdata(lines)
        del lines
```



单个脚本限制内存：避免脚本将剩余内存全部使用完

```python
def limit_memory(maxsize):
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))
# 单位字节
limit_memory(2*1024*1024*1024)
```





*如果觉得本文对你有所帮助，欢迎点击右上角GitHub图标给个Star呗~*