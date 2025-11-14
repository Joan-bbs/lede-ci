#!/bin/bash

# 修改默认 IP
sed -i 's/192.168.1.1/192.168.2.200/g' package/base-files/files/bin/config_generate

# bash 替换 ash
sed -i '1s/ash/bash/' package/base-files/files/etc/passwd

# 生成编译时间
date "+%Y-%m-%d %H:%M:%S %z" >> package/base-files/files/etc/build_date
