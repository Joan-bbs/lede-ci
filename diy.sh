#!/bin/bash

# 修改默认 IP
sed -i 's/192.168.1.1/192.168.8.1/g' package/base-files/files/bin/config_generate

# 修改本地时间格式的显示
sed -i 's/os.date()/os.date("%a %Y-%m-%d %H:%M:%S")/g' package/lean/autocore/files/*/index.htm

# 添加design主题和插件包
# git clone https://github.com/gngpp/luci-theme-design.git package/luci-theme-design
# git clone https://github.com/gngpp/luci-app-design-config.git package/luci-app-design-config

# 添加argon主题和插件包
# git clone -b 18.06 https://github.com/jerrykuku/luci-theme-argon.git package/luci-theme-argon
# git clone -b 18.06 https://github.com/jerrykuku/luci-app-argon-config.git package/luci-app-argon-config
