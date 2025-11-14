#!/bin/bash

# 修改默认 IP
sed -i 's/192.168.1.1/192.168.2.1/g' package/base-files/files/bin/config_generate

# bash 替换 ash
sed -i '1s/ash/bash/' package/base-files/files/etc/passwd

# 生成编译时间
date "+%Y-%m-%d %H:%M:%S %z" >> package/base-files/files/etc/build_date
sed -i "s|DISTRIB_REVISION='.*'|DISTRIB_REVISION='R$(date +%Y.%m.%d)'|g" package/lean/default-settings/files/zzz-default-settings
