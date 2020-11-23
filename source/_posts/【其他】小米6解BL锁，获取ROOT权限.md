---
title: 【其他】小米6解BL锁，获取ROOT权限
top: false
cover: false
toc: true
mathjax: true
date: 2020-11-01 14:35:56
password:
summary: 最近换手机，想把之前一直用的小米6给 root 了，刷个机方便之后折腾。
tags:
- 其他
- 刷机
categories:
- 折腾

---

## 前言

最近换手机，想把之前一直用的小米6给 root 了，刷个机方便之后折腾。

小米有一点我比较喜欢的就是至今（2020年11月7日）还有官方解锁渠道，手里有旧手机，或者就是想折腾的人也能有较为方便的获取 root 权限的途径（安卓手机拿到 root 权限，可就想怎么折腾都可以了）。

不过在 root 小米6的过程中也遇到了许多问题，这里记录一下给需要的同学一个参考。



## 基本环境

手机：小米6 

手机系统版本：MIUI11.0.5.0 稳定版

<img src="手机系统信息.jpg" alt="手机系统信息" style="zoom:50%;" />



操作的电脑系统版本：

```powershell
版本	Windows 10 专业版
版本号	20H2
安装日期	‎2020/‎6/‎25
操作系统版本	19042.610
体验	Windows Feature Experience Pack 120.2212.31.0
```



## 解BL锁

### 正常流程下步骤

1. 先阅读下[小米手机解锁 Bootloader 教程以及常见问题](https://www.xiaomi.cn/post/4378807) ，了解下解锁 Bootloader 的基本步骤
2. 手机上操作，“设置 - 我的设备 - 所有参数” 连续按 MIUI版本，进入开发者模式
3. 手机上操作，“设置 - 更多设置 - 开发者选项 - 设备解锁状态”，进行账号绑定和确认状态

<img src="设备解锁状态-未解锁.jpg" alt="设备解锁状态-未解锁" style="zoom:50%;" />



**注意：这个步骤需要断开wifi，使用手机流量操作。且账号要与步骤5中登录账号一致**

4. 下载小米解锁工具，[中文版](http://www.miui.com/unlock/download.html)，[英文版](https://en.miui.com/unlock/download_en.html)

<img src="下载小米解锁工具.png" alt="下载小米解锁工具" style="zoom:80%;" />

5. 打开小米解锁工具，登录小米账号

<img src="登录小米解锁工具.png" alt="登录小米解锁工具" style="zoom:60%;" />

6. 按照提示将手机关机后，长按音量下键 + 电源键进入 FastBoot 页面

7. 安装驱动。要么将手机连接到电脑后自动安装好驱动，要么在小米解锁工具的设置页面手动安装驱动

<img src="安装驱动.png" alt="安装驱动" style="zoom:60%;" />

8. 若是一切正常，这时候解锁工具页面应该是以下样子（我没有这么幸运能一次成功）

<img src="手机连接上解锁工具.png" alt="手机连接上解锁工具" style="zoom:60%;" />

9. 点击解锁。**注意：解锁会将手机恢复出厂设置，请提前备份数据**

<img src="准备开始解锁.png" alt="准备开始解锁" style="zoom:60%;" />

10. 等待解锁完成

<img src="解锁到95.png" alt="解锁到95%" style="zoom:60%;" />



<img src="解锁成功.png" alt="解锁成功" style="zoom:60%;" />

11. 等到手机重启后查看 “设置 - 更多设置 - 开发者选项 - 设备解锁状态” （在开机的时候屏幕下方会有“unlock”字符）

<img src="解锁完成后手机状态.jpg" alt="解锁完成后手机状态" style="zoom:50%;" />



### 遇到的问题

- 问题一：手机连接上电脑后，在解锁工具中检测不到设备

<img src="检测不到手机.png" alt="检测不到手机" style="zoom:80%;" />

尝试解决：

1. 换线，换USB接口，都无效

2. 卸载驱动后重新安装，无效
3. 换了另一台win10的电脑尝试，问题仍存在

4. 只能通过重启电脑后才能检测到设备，如果重启后拔插了usb，又检测不到了



- 问题二：开始解锁后，验证设备信息到50%后验证失败（重启电脑后解锁工具能检测到手机，此时可以点击解锁）

<img src="50验证失败.png" alt="50验证失败" style="zoom:80%;" />

尝试解决：

1. 换了老版本解锁工具，无效

2. 参考[小米解锁无法获取手机信息解决方法](https://miuiver.com/unable-to-get-phone-info/)，换英文版的解锁工具，无效

3. 根据问题一需要重启解锁工具才能显示检测到手机推测应该是驱动有问题。参考 https://www.52pojie.cn/forum.php?mod=viewthread&tid=905825&archive=1&extra=page%3D1&page=2  中提到的解决方法继续以下的尝试解决方法

4. 使用 [小米助手3.0](http://zhushou.xiaomi.com/)  安装驱动，使用原装线，无效

5. 使用 [搞机助手](https://www.52pojie.cn/forum.php?mod=viewthread&tid=1169553&highlight=%B8%E3%BB%FA%D6%FA%CA%D6) 小米usb3.0 修复补丁，安装后重启电脑，再使用解锁工具解锁，【 成功】

<img src="搞机助手安装修复补丁.png" alt="搞机助手安装修复补丁" style="zoom:80%;" />

6. 下载360手机管家安装安卓驱动，未测试
7. 换win7系统，再使用解锁工具安装驱动解锁，未测试



其他参考：

- [BL锁解锁失败必看](https://www.mi.com/service/special/BL-loc)

- [小米 9 解 bl 锁,在 fastboot 界面，解锁工具始终显示未连接](https://www.v2ex.com/t/589868)



## 线刷开发版系统

1. [通过线刷升级](http://www.miui.com/shuaji-393.html)，下载通用刷机工具
2. [小米全系列机型刷机包下载站汇总（长期更新）](https://www.xiaomi.cn/post/5896315)，查找对应的系统包（我这里下载的是 9.8.22（9.0） 的线刷包，当前系统里面升级页面找不到卡刷包的入口）。说明：应官方要求，9.9.3版本往后暂不提供开发版下载方式，请大家移步[内测中心](https://web-alpha.vip.miui.com/page/info/mio/mio/internalTest?type=2)申请开发板公测/内侧体验。

3. 在手机上操作：关机状态下，同时按住 音量下+电源键 进入Fastboot模式将手机USB连接电脑

4. 线刷包下载完成后解压，打开线刷包文件夹，复制地址栏地址到刷机工具中，点击刷机

<img src="线刷中.png" alt="线刷中" style="zoom:80%;" />

5. 等待刷机完成。手机刷机完后会重启，第一次启动的时间有点久的，别以为是刷成砖了，耐心等待下。注意：这里有个坑爹的地方：默认情况下，解了BL锁右下角会选择全部删除并lock，这样线刷完后BL又锁上了。需要手动选择下全部删除选项

<img src="线刷完成.png" alt="线刷完成" style="zoom:80%;" />

6. 查看手机是否已经是开发版本了

<img src="刷到开发板.jpg" alt="刷到开发板" style="zoom:60%;" />



## 开启ROOT权限

参考[【原创】小米手机获取完整ROOT权限教程](https://www.xiaomi.cn/post/4471505)

1. 打开手机管家

<img src="root1.png" alt="打开手机管家" style="zoom:60%;" />

2. 点击应用管理

<img src="root2.png" alt="点击应用管理" style="zoom:60%;" />

3. 点击权限

<img src="root3.png" alt="点击权限" style="zoom:60%;" />

4. 点击开启ROOT权限

<img src="root4.png" alt="点击开启" style="zoom:60%;" />

5. 开启ROOT。注意：需要网络连接，成功后会重启。如果更新了开发版系统，需要重新再开启ROOT

<img src="root5.png" alt="开启ROOT" style="zoom:60%;" />

6. 解锁System分区。系统提供的ROOT功能并不是完整的；要获取完整的权限，必须解锁System分区！下载 [Syslock](https://www.coolapk.com/apk/com.lerist.syslock)，开启解锁后重启即可生效。（应用获取ROOT权限也提示太多次了吧，每次都要等待5s）

<img src="获取root权限提示太多.jpg" alt="获取root权限提示太多" style="zoom:50%;" />



<img src="解锁system.jpg" alt="解锁system" style="zoom:50%;" />



### 刷入TWRP

如果需要刷入TWRP，可以参考以下步骤。能获取ROOT权限应该开发版也够用了。如果刷第三方，还是可以装下TWRP

1. 下载TWRP。到 [TWRP设备列表](https://twrp.me/Devices/) 中找到小米（[Xiaomi](https://twrp.me/Devices/Xiaomi/)），进入找到[小米6机型](https://twrp.me/xiaomi/xiaomimi6.html)。

<img src="下载TWRP.png" alt="下载TWRP" style="zoom:80%;" />

2. 手机开启USB调试模式
3. 打开搞机助手

<img src="打开搞机助手.png" alt="打开搞机助手" style="zoom:80%;" />

4. 点击系统模式下重启到引导模式，或者直接音量下+电源键进入

<img src="刷入REC.png" alt="刷入REC" style="zoom:80%;" />

5. 选择刚才下载的img

<img src="刷入REC1.png" alt="选择刚下载的文件" style="zoom:80%;" />

6. 等待刷入成功，默认会重启进入引导模式

<img src="刷入REC成功.png" alt="刷入REC成功" style="zoom:80%;" />





*如果觉得本文对你有所帮助，欢迎点击右上角GitHub图标给个Star呗~*