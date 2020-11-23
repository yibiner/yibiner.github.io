---
title: 【Unraid】NAS 小主机配置分享
top: true
cover: false
toc: true
mathjax: true
date: 2020-10-8 00:18:38
password:
summary: 分享下个人用的 unraid 小主机以及一些配置
tags:
- Unraid
- NAS
categories:
- 折腾
---



## 硬件配置

|        | 名称                         | 价格    | 说明                                                         |
| ------ | ---------------------------- | ------- | ------------------------------------------------------------ |
| 主板   | 铭瑄的H81 itx                | 150     | 建议买之前确认下网卡是百兆的还是千兆，要是不在意那就无所谓   |
| 内存   | 三星 ddr3 8gx2               | 240     | 上16g的内存是因为用得上，unraid 系统运行时内存占用很少       |
| CPU    | i3-4160T/E3-1265L v3         | 195/520 | 计划是7*24 运行，所以CPU只考虑低功耗的了。整机加上两个机械硬盘，一个固态硬盘功耗正常运行时大概在20W |
| 机箱   | 万由代工的暴风酷播云二代机箱 | 175     | 血亏的机箱，矿灾后的产物。双盘位                             |
| 散热器 | 大镰刀S950M                  | 44      | 高31mm。                                                     |
| 网卡   | AX88179 USB3.0 千兆网卡      | 40      | 主板上的网卡是百兆的，拓展一个千兆网卡， 局域网下千兆还是舒服点。使用usb的网卡主要是因为机箱大小不支持pcie类型的，这块网卡确认unraid 免驱 |
| U盘    | 随便                         |         | 最好用品牌的U盘，其他便宜U盘有可能会在做系统的时候出问题。如果正常做了启动盘后，系统起不来，那最好换个U盘试下 |

以上的价格都是2020年1月左右的，部分全新，部分二手



## 重启不丢配置及项目文件说明

### 重启不丢配置

unraid 系统默认会在重启时，恢复默认设置。如果安装了oh-my-zsh ，重启后会发现什么都没了，这时候可以参考插件的做法，将修改后的配置文件拷贝到 /boot 目录下，然后在启动脚本中恢复下个人配置。 unraid 系统的启动脚本 `/boot/config/go` 。



重启不丢配置可以参考个人当前unraid恢复配置项目 [custom.scripts](https://github.com/yibiner/custom.script) 

直接将项目clone到 `/boot/config`下，在 `/boot/config/go` 文件中最后添加 

```shell
cp -r /boot/config/custom.scripts /tmp
bash /tmp/custom.scripts/startall.sh
```



### 项目文件说明

- config.sh 配置文件。
- commfunc.sh 公共函数文件。一些日志输出函数。

- startall.sh 运行所有设置配置脚本的入口。会运行所有 set 开头的脚本文件，会 nohup 运行 loop 开头的脚本文件，这样后续添加设置文件更加清晰。
- updateconfig.sh 将一些配置保存到U盘中
- setddns.sh 定时检查外网ip
- setohmyzsh.sh 恢复oh-my-zsh
- setssh.sh 恢复ssh 的配置，禁用密码登录、重启sshd 等
- setplugins.sh autofan设置风扇根据CPU温度调节
- setroute.sh 设置路由



## Oh My Zsh 安装

- 先安装了zsh
  - 在 APPS 中搜索并安装 Nerd Pack
  - 在 SETTINGS -> Nerd Pack 中安装 zsh
- 安装oh-my-zsh

```shell
# curl 安装
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
# wget 安装
sh -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"
```

- `bash /tmp/updateconfig.sh` 执行下脚本，将当前的设置和文件保存到 `/boot` 下，方便重启后恢复

```shell
# 项目 custom.scripts(https://github.com/yibiner/custom.script)  中 恢复oh-my-zsh
$ cat setohmyzsh.sh 
#!/bin/bash

# 将 oh-my-zsh 解压到目录
if [ ! -d /root/.oh-my-zsh  ] ; then
    tar -zxvf oh-my-zsh.tar.gz -C /root
fi

# 将配置文件拷贝回目录
cp $BASE_PATH/.bash* /root
cp $BASE_PATH/.zsh* /root
```



## SSH 密钥登录并关闭密码登录

- 命令行下执行 `ssh-keygen -t rsa -C "your_email@example.com"` 生成密钥对
- 将`~/.ssh/id_rsa.pub` 公钥添加到unraid 的 `~/.ssh/authorized_keys` 中。如果没有 .ssh 目录和 authorized_keys 文件，自己新建即可，authorized_keys 文件权限为 644。

- 关闭密码登录。 `/etc/ssh/sshd_config` 将 `PasswordAuthentication yes` 改成 `PasswordAuthentication no`。重启下sshd即可生效
- `bash /tmp/updateconfig.sh` 执行下脚本，将当前的设置和文件保存到 `/boot` 下，方便重启后恢复

```shell
# 项目 custom.scripts (https://github.com/yibiner/custom.script) 中 恢复ssh，将配置文件覆盖原有的配置后，重启服务
$ cat setssh.sh 
#!/usr/bin/bash

# 从boot中恢复ssh文件

ssh_start()                                                                                        
{                                                                                                  
  # no-op if already running                                                                       
  if [ -f /var/run/sshd.pid ]; then                                                                
    #echo "SSH already running"                                                                    
    #sleep 1                                                                                       
    return                                                                                         
  fi                                                                                               
                                                                                                   
  echo "Starting SSH..."                                                                           
  sleep 1                                                                                          
                                                                                                   
  /usr/sbin/sshd                                                                                   
                                                                                                   
  echo "... OK"                                                                                    
  sleep 1                                                                                          
}                                                                                                  
                                                                                                   
ssh_stop()                                                                                         
{                                                                                                  
  # no-op if already running                                                                       
  if [ ! -f /var/run/sshd.pid ]; then                                                              
    #echo "SSH already stopped"                                                                    
    #sleep 1                                                                                       
    return                                                                                         
  fi                                                                                               
                                                                                                   
  echo "Stopping SSH..."                                                                           
  sleep 1                                                                                          
                                                                                                   
  killall sshd                                                                                     
                                                                                                   
  echo "... OK"                                                                                    
  sleep 1                                                                                          
}                                                                                                  
                                                                                                   
ssh_restart() {                                                                                    
  if [ -r /var/run/sshd.pid ]; then                                                                
    echo "Restarting parent listener process only. To kill every sshd process, you must use stop"  
    sleep 3                                                                                        
    kill `cat /var/run/sshd.pid`                                                                   
  else                                                                                             
    echo "Warning: there does not appear to be a parent instance of sshd running."                 
    sleep 3                                                                                        
    exit 1                                                                                         
  fi                                                                                               
  sleep 1                                                                                          
  ssh_start                                                                                        
}


if [ -d "/root/.ssh" ]; then
  cp $BASE_PATH/.ssh/* /root/.ssh/
fi

if [ ! -d "/root/.ssh" ]; then
  cp -r $BASE_PATH/.ssh /root
fi
chmod 644 /root/.ssh/id_rsa.pub
chmod 644 /root/.ssh/authorized_keys

cp $BASE_PATH/sshd_config /etc/ssh/sshd_config
ssh_restart

```



## CPU 风扇根据CPU温度动态调节转速

- unraid 管理页面 APPS 下搜索 autofan 安装 Dynamix System **Autofan**
- 然后在 SETTINGS -> Fan Auto Control 里 Enabled 该功能，需要注意下 PWM controller 和 PWM fan 是否选到了对应的设备。
- Minimum PWM value 设置最小转速PWM，最大值是255
- Low temperature threshold 温度下限阈值， High temperature threshold  温度上限阈值
- 修改 `/usr/local/emhttp/plugins/dynamix.system.autofan/scripts/autofan` ，根据CPU温度添加转速， 默认是根据硬盘温度

```shell
# 完整见项目 custom.scripts (https://github.com/yibiner/custom.script) 中的 autofan 
function_get_current_cpu_temp() {
    HIGHEST_TEMP=0
    HIGHEST_TEMP=`sensors | grep "CPU Temp" | awk '{print $3}' | tr -cd "[0-9.]" | sed "s/\..*//g"`
}
```

 

```shell
# 项目 custom.scripts (https://github.com/yibiner/custom.script) 中 设置autofan
$ cat setplugins.sh 
#!/usr/bin/bash

# autofan 修改为根据 CPU 温度调节转速
filename=/usr/local/emhttp/plugins/dynamix.system.autofan/scripts/autofan
if [ -e $filename ] ; then
    # sed -i 'N;196afunction_get_current_cpu_temp() {\nHIGHEST_TEMP=0\nHIGHEST_TEMP=`sensors | grep "CPU Temp" | awk "{print $3}" | tr -cd "[0-9.]" | sed "s/\..*//g"`\n}' $filename
    # sed -i 'N;292afunction_get_current_cpu_temp' $filename
    # sed -i '292 d' $filename
    cp $BASE_PATH/autofan $filename
    /usr/local/emhttp/plugins/dynamix.system.autofan/scripts/rc.autofan restart
fi
```



## 双网卡同一局域网设置

```shell
$ cat setroute.sh
#!/usr/bin/bash

# 设置百兆、千兆网卡走不同路由，互不影响
hadlan=`grep "lan" /etc/iproute2/rt_tables`
# 新建一个编号为200 ，名字为lan的路由表
if [ -z "$hadlan" ] ; then
    echo "200 lan" >> /etc/iproute2/rt_tables
fi

# 删除default路由表中千兆网的配置
had1G=`ip route list | grep "192.168.1.0/24 dev br1 proto dhcp scope link src 192.168.1.5"`
if [ -n "$had1G" ] ; then
    ip route del 192.168.1.0/24 dev br1 proto dhcp scope link src 192.168.1.5 metric 215
fi

# 往 lan 路由表 中新增路由
had1G=`ip route list table lan | grep "192.168.1.5"`
if [ -z "$had1G" ] ; then
    ip route add 192.168.1.0/24 dev br1 proto dhcp scope link src 192.168.1.5 metric 215 table lan
fi

# 设置千兆网卡流量只看 lan 路由表
had1G=`ip rule | grep "from 192.168.1.5 lookup lan"`
if [ -z "$had1G" ] ; then
    ip rule add from 192.168.1.5 table lan
fi
```

多网卡连接同一局域网时， 不做设置下是只会走一个物理链路的，默认路由就是这样。这里将两个IP的路由区别开来，这样就能实现访问不同IP走的是不同的物理链路，具体细节请搜索 linux 高级路由设置。



## DNSPod 实现 ddns

- https://console.dnspod.cn/dns/list 注册个域名
- https://console.dnspod.cn/account/token 账号中心 -> 密钥管理，创建个密钥
- [custom.scripts](https://github.com/yibiner/custom.script)  项目中 dns.conf 文件中填入创建的密钥对



### ddns脚本修改

脚本参考  https://github.com/imki911/ArDNSPod，做了以下修改，见  [ddnspod.sh](https://github.com/yibiner/custom.script/blob/master/ddnspod.sh)：

- 获取本机的外网IP时，循环遍历几个能通过curl直接获取外网IP的网址，避免因为某个网址打不开而失败（是的，我经历过
- 将上次的外网IP记录在本地文件，而不是每次都去网页获取上次的IP记录



### 使用 cron 设置定时，每10分钟检查一次

```shell
# 项目 custom.scripts (https://github.com/yibiner/custom.script) 中设置ddns，参考了dynamix.schedules  的思路
$ cat setddns.sh 
#!/bin/bash

crontab -l > /tmp/cron.tmp
echo "*/10 * * * * bash /tmp/custom.scripts/onetimeddns.sh" >> /tmp/cron.tmp
crontab /tmp/cron.tmp
```



若是频率能接受每小时检查一次， 可以参考下文。将脚本放到 `/etc/cron.hourly/` 目录下即可，需要安装 `dynamix.schedules`插件

```shell
# cp /tmp/custom.scripts/runddns.sh /etc/cron.hourly/
# chmod +x /etc/cron.hourly/runddns.sh
```



## 山克UPS不间断电源配置

一个合格的NAS主机，注定了是要7*24小时不间断工作的，可是呢，谁也保不准家里什么时候会断电（组完机器的一个月内我就遇到了两次无预警断电）。所以呢，一个UPS就很重要了，可以让NAS在断电后能主动关机。

入了最便宜的山克UPS 600VA的那款。

顺带一提，UPS本身的功耗就10多W了。

unraid 的 SETTINGS 中有UPS Setting ，直接支持一系列的UPS。不过山克这款尝试过后并不能直接支持，不确定是不是我设置有问题。

所以当前使用了个折中方案，通过ping 家里路由器判断是否断电。详细见 [loopping4ups.sh](https://github.com/yibiner/custom.script/loopping4ups.sh)





*如果觉得本文对你有所帮助，欢迎点击右上角GitHub图标给个Star呗~*