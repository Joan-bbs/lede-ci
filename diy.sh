#!/bin/bash

# 修改默认主题
sed -i 's/luci-theme-bootstrap/luci-theme-material/g' feeds/luci/collections/luci-light/Makefile

# 修改默认 IP
sed -i 's/192.168.1.1/192.168.2.1/g' package/base-files/files/bin/config_generate

# ttyd 免帐号登录
sed -i 's/\/bin\/login/\/bin\/login -f root/' feeds/packages/utils/ttyd/files/ttyd.config

# bash 替换 ash
sed -i '1s/ash/bash/' package/base-files/files/etc/passwd

# 添加 luci-app-tailscale
sed -i '/\/etc\/init\.d\/tailscale/d;/\/etc\/config\/tailscale/d;' feeds/packages/net/tailscale/Makefile
git clone --depth 1 https://github.com/asvow/luci-app-tailscale package/luci-app-tailscale

# 修改 luci-app-cpufreq
sed -i 's/CPU 性能优化调节/CPU 性能调节/g' feeds/luci/applications/luci-app-cpufreq/po/zh_Hans/cpufreq.po

# 设置默认 root 密码为 password
sed -i 's/root:::0:99999:7:::/root:$1$V4UetPzk$CYXluq4wUazHjmCDBCqXF.::0:99999:7:::/g' package/base-files/files/etc/shadow

# 生成编译时间
date "+%Y-%m-%d %H:%M:%S %z" >> package/base-files/files/etc/build_date
sed -i "s/OPENWRT_RELEASE=\".*\"/OPENWRT_RELEASE=\"%D %V $(date '+%Y.%m.%d')\"/g" package/base-files/files/usr/lib/os-release

# 修改首页显示
rm -rf feeds/luci/modules/luci-mod-status/htdocs/luci-static/resources/view/status/include/40_dhcp.js
curl -o feeds/luci/modules/luci-mod-status/htdocs/luci-static/resources/view/status/include/40_dhcp.js https://raw.githubusercontent.com/y9858/Home-mod/refs/heads/main/40_dhcp.js
rm -rf feeds/luci/modules/luci-mod-status/htdocs/luci-static/resources/view/status/index.js
curl -o feeds/luci/modules/luci-mod-status/htdocs/luci-static/resources/view/status/index.js https://raw.githubusercontent.com/y9858/Home-mod/refs/heads/main/index.js

rm -rf feeds/packages/net/speedtest-cli
git clone --depth 1 https://github.com/sbwml/openwrt_pkgs.git package/new/custom
mv package/new/custom/luci-app-netspeedtest  package/new
mv package/new/custom/speedtest-cli package/new
rm -rf package/new/custom

WIFI_SH=$(find ./target/linux/{mediatek/filogic,qualcommax}/base-files/etc/uci-defaults/ -type f -name "*set-wireless.sh" 2>/dev/null)
WIFI_UC="./package/network/config/wifi-scripts/files/lib/wifi/mac80211.uc"
WRT_SSID=LibWrt
WRT_WORD=12345678
if [ -f "$WIFI_SH" ]; then
	#修改WIFI名称
	sed -i "s/BASE_SSID='.*'/BASE_SSID='$WRT_SSID'/g" $WIFI_SH
	#修改WIFI密码
	sed -i "s/BASE_WORD='.*'/BASE_WORD='$WRT_WORD'/g" $WIFI_SH
elif [ -f "$WIFI_UC" ]; then
	#修改WIFI名称
	sed -i "s/ssid='.*'/ssid='$WRT_SSID'/g" $WIFI_UC
	#修改WIFI密码
	sed -i "s/key='.*'/key='$WRT_WORD'/g" $WIFI_UC
	#修改WIFI地区
	sed -i "s/country='.*'/country='CN'/g" $WIFI_UC
	#修改WIFI加密
	sed -i "s/encryption='.*'/encryption='psk2+ccmp'/g" $WIFI_UC
fi
