#!/bin/bash

# 修改默认 IP
sed -i 's/192.168.1.1/192.168.8.1/g' package/base-files/files/bin/config_generate

# 修改本地时间格式的显示
sed -i 's/os.date()/os.date("%a %Y-%m-%d %H:%M:%S")/g' package/lean/autocore/files/*/index.htm

# 移除 openwrt feeds 自带的核心库
rm -rf feeds/packages/net/{xray-core,v2ray-geodata,sing-box,chinadns-ng,dns2socks,hysteria,ipt2socks,microsocks,naiveproxy,shadowsocks-libev,shadowsocks-rust,shadowsocksr-libev,simple-obfs,tcping,[...]} 2>/dev/null || true

# 清理旧的 passwall 目录，避免重复或冲突
rm -rf package/passwall-packages package/passwall-luci package/passwall2-luci

# 拉取 passwall packages（不要默认最新）
git clone https://github.com/Openwrt-Passwall/openwrt-passwall-packages package/passwall-packages
cd package/passwall-packages
# 如需锁定到某个固定 commit，取消下面一行注释并填入 commit
# git checkout <固定commit>
cd -

# 移除 openwrt feeds 里旧的 luci 版本
rm -rf feeds/luci/applications/luci-app-passwall

# 锁定 passwall 和 passwall2 的版本
git clone -b 25.11.15-1 https://github.com/Openwrt-Passwall/openwrt-passwall package/passwall-luci
git clone -b 25.11.18-1 https://github.com/Openwrt-Passwall/openwrt-passwall2 package/passwall2-luci

# 添加design主题和插件包
git clone https://github.com/gngpp/luci-theme-design.git package/luci-theme-design
git clone https://github.com/gngpp/luci-app-design-config.git package/luci-app-design-config

# 添加argon主题和插件包
git clone -b 18.06 https://github.com/jerrykuku/luci-theme-argon.git package/luci-theme-argon
git clone -b 18.06 https://github.com/jerrykuku/luci-app-argon-config.git package/luci-app-argon-config
