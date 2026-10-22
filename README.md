## 特别提示 [![](https://img.shields.io/badge/-个人免责声明-FFFFFF.svg)](#特别提示-)

- **本人不对任何人因使用本固件所遭受的任何理论或实际的损失承担责任！**

- **本固件禁止用于任何商业用途，请务必严格遵守国家互联网使用相关法律规定！**

## 项目说明 [![](https://img.shields.io/badge/-项目基本介绍-FFFFFF.svg)](#项目说明-)
- 固件默认管理地址：`192.168.8.1` 默认用户：`root` 默认密码：`password`

## PassWall 固定版本编译

X86-64 和 NanoPi-R3S 工作流均使用以下源码版本：

| 软件包 | 版本 / 上游 tag | 固定 commit |
| --- | --- | --- |
| luci-app-passwall | 25.11.15-1 | 97d69ab5becbda354e2d3ea5004f09b4db275375 |
| luci-app-passwall2 | 25.11.18-1 | dbf48fb5bd9f6e68824800cf418265b42c943c7d |

原配置虽然指定了 tag，但 `luci` feed 也提供同名包，且位于它们之前。
`feeds install -a` 会优先使用先安装的同名包，因此不能仅凭拉取了 tag 判断实际编译版本。

现在使用 `URL^commit` 固定源码，并将这两个 feed 放在 `luci` 前面；工作流先卸载旧链接，
再用 `install -f -p` 安装指定来源，最后安装其余 feeds。工具链缓存也使用新的命名空间，
并包含 feeds、版本检查脚本和设备配置的哈希。

编译前检查实际源码链接、commit、Makefile 版本和 `.config` 的 `=y` 选择；编译后检查每个固件
manifest 内的实际安装版本和生成的 IPK 文件版本。任何检查失败都会停止，禁止上传或发布。
成功时 Actions 摘要及固件附件 `passwall-versions.txt` 会记录版本和源码提交。
新版 `luci.mk` 可能将包版本写为 `25.11.15-r1` / `25.11.18-r1`；
`r1` 与 `1` 均表示上游的第 1 次打包，检查允许这两种格式，其他版本或 release 均不允许。

使用方法：打开 **Actions → X86-64 或 NanoPi-R3S → Run workflow**，
在分支下拉框选择 **fix/pin-passwall-versions** 后运行。不要选择 `main` 或重跑旧提交的任务。
Release tag 将指向本次工作流实际使用的提交。

以后升级时，同时更新 `feeds.conf.default` 中的 commit 和 `scripts/check-passwall.py` 中的
`LOCKS`，核对上游 Makefile 的 `PKG_VERSION`、`PKG_RELEASE` 后重新编译。
这里锁定的是两个 LuCI 插件版本；代理核心和其他依赖仍由现有 feeds 提供，未锁定整个固件依赖树。

## 工作流编译内容与备注

下面根据仓库配置、指定的两个 PassWall tag 以及检查时的 LEDE/LuCI 源码整理。
配置是精简配置，`make defconfig` 会自动补齐默认包、依赖和子选项；因此“明确选中”与
“依赖/默认带入”分开列出。feeds 拉取不等于把整个 feed 的所有软件都编译。

### 两个配置明确选中的插件

| 包名 | X86-64 | NanoPi-R3S 工作流的配置 | 用途与备注 |
| --- | --- | --- | --- |
| luci-app-passwall | y | y | PassWall，固定 25.11.15-1，代理管理页面及脚本 |
| luci-app-passwall2 | y | y | PassWall2，固定 25.11.18-1；与 PassWall 共用部分核心和依赖 |
| luci-app-turboacc | y | y | 网络加速设置；实际加速引擎和 BBR 由当前 feed 的子选项决定 |
| luci-app-filetransfer | y | y | 网页文件上传、下载 |
| luci-app-autoreboot | y | y | 定时重启 |
| luci-app-arpbind | y | y | IP/MAC 绑定 |
| luci-app-ttyd | y | y | 网页终端，依赖 ttyd |
| luci-app-diskman | y | y | 磁盘、分区、文件系统管理；会增加磁盘工具和文件系统模块 |
| luci-app-firewall | y | y | 防火墙管理页面 |
| luci-app-design-config | n | y | Design 主题设置 |
| luci-theme-design | n | y | Design 主题 |
| luci-theme-argon | n | y | Argon 主题；其设置插件 luci-app-argon-config 两边均未选中 |

两个配置中 `luci-app-turboacc_INCLUDE_PDNSD=y` 是旧字段，检查时的 TurboACC 源码已没有这个
配置项，不能据此认为 PDNSD 一定会编译。原字段保留并加注释，未擅自更换 DNS 方案。

### PassWall 会带入的组件

| 类别 | 组件 | 备注 |
| --- | --- | --- |
| 直接依赖 | coreutils、coreutils-base64、coreutils-nohup、curl、ip-full、Lua、libuci-lua、luci-compat、luci-lib-jsonc、resolveip、tcping | 两个插件的运行基础工具/库；构建系统会合并公共依赖 |
| PassWall 直接依赖 | chinadns-ng、dns2socks、dnsmasq-full、microsocks | DNS 分流、DNS 转发、SOCKS 等辅助程序 |
| PassWall2 直接依赖 | xray-core、geoview、v2ray-geoip、v2ray-geosite、unzip | Xray 核心、规则查询工具和路由数据；Geo 数据不等于额外安装 V2Ray 核心 |
| 两个 tag 的默认子选项 | haproxy、sing-box、shadowsocks-libev-ss-local/ss-redir、shadowsocksr-libev-ssr-local/ssr-redir、simple-obfs-client、v2ray-plugin | 在满足架构/依赖条件时自动选中；当前设备配置没有逐项覆盖这些开关 |
| PassWall 默认子选项 | trojan-plus、shadowsocks-libev-ss-server、shadowsocks-rust-sslocal、geoview、xray-core | Rust 客户端默认针对 aarch64/x86_64；其他组件也有各自的架构条件 |
| 默认关闭的可选功能 | hysteria、naiveproxy、tuic-client、shadow-tls、shadowsocks-rust-ssserver、shadowsocksr-libev-ssr-server、xray-plugin | 两个设备配置没有显式打开；仍可能由其他包选择，最终以生成配置为准 |
| 透明代理相关依赖 | iptables/ipset/ipt2socks 或 nftables，及对应的 tproxy/socket/NAT 内核模块 | 按 firewall4 与插件子选项选择，不能将两套全部视为必选项 |

固定 LuCI 插件 tag 不会同时固定 xray-core、sing-box 等核心版本，核心仍来自现有 packages 等 feeds。
同一个核心被两个插件依赖时通常构建一份；“编译进固件”也不代表服务会自动同时启动。

### 系统和硬件相关内容

| 类别 | 编译内容与用途 | 备注 |
| --- | --- | --- |
| 基础系统 | Linux 内核、BusyBox、procd、netifd、ubus、uci、opkg、fstools、logd 等 | 系统启动、网络、配置、日志和包管理所需，会补齐库依赖 |
| 路由功能 | DNS/DHCP、防火墙、PPP/PPPoE、IPv6、连接跟踪、NAT、隧道等 | 来自目标默认包、内核配置和插件依赖；最终配置决定准确清单 |
| 管理界面 | LuCI、rpcd、uhttpd、默认 Bootstrap 主题及相关库 | `luci-app-uhttpd=n` 只是不装它的设置页面，不等于删除 uhttpd 网页服务器 |
| X86 硬件支持 | Intel/AMD 微码、多种有线/USB/虚拟网卡、存储、传感器等驱动；目标默认还含音频和显卡模块 | x86 默认包较多，不是只编译 PassWall；未在本次修改中裁剪硬件驱动 |
| X86 镜像设置 | x86_64 generic、SquashFS、UEFI 启动镜像 | 显式关闭 Ext4 根文件系统镜像及传统 GRUB 镜像；实际镜像文件以输出为准 |
| ARM 配置 | 原文件选择 armvirt/64 generic、SquashFS | 这是旧的通用 ARM64 配置，并不是 NanoPi R3S 专用设备配置 |
| 编译机工具 | 交叉编译工具链、宿主工具、Go/Rust 等依赖工具（按实际包需要） | 不等于在路由器中安装这些完整开发环境；可复用工具链缓存 |

重要发现：工作流名叫 `NanoPi-R3S`，但配置的 `CONFIG_TARGET_armvirt*` 不匹配设备名称。
检查时 LEDE 已提供 `rockchip/armv8/friendlyarm_nanopi-r3s`，且旧 `armvirt` 目标已不存在。
用当前 master 执行 `make defconfig` 可能丢弃旧目标并改变选择，不能把该工作流的产物认作 R3S 专用刷机镜像。
本次仅为其加注释，未未经确认更换硬件目标。

工作流跟随 LEDE `master`，其他 feeds 也没有固定提交，因此内核、驱动及其他插件版本会随上游变化。
原 Release 文案中的固定“6.8 kernel”已删除，避免与实际内核不符。

### 配置中明确关闭的常见插件

| 类别 | 未选中的插件 | 备注 |
| --- | --- | --- |
| 其他代理 | OpenClash、SSR Plus、HomeProxy、VSSR、V2Ray Server | 不安装这些 LuCI 插件；PassWall 仍可带入共享代理核心 |
| VPN/组网 | WireGuard 页面、OpenVPN Server、IPsec、SoftEther、ZeroTier、n2n、PPTP Server | 未选中对应 LuCI 插件，不代表所有协议库或内核模块均不存在 |
| 容器/下载 | Dockerman、Aria2、qBittorrent、Transmission、Alist | 未选中对应 LuCI 插件；Dockerman 关闭不能单独作为 Docker 核心不存在的证明 |
| DNS/过滤 | AdGuardHome、SmartDNS、Adbyby、ikoolproxy、OAF | 不安装对应 LuCI 插件；dnsmasq-full、chinadns-ng 仍会被依赖带入 |
| 穿透/远程 | FRPC、FRPS、NPS、Socat、ddnsto | 未选中对应页面/插件 |
| 文件/共享 | Samba4、NFS、vsftpd、rclone、KodExplorer、FileBrowser、CIFS 挂载、Verysync | 不安装这些应用页面；filetransfer 和 diskman 仍启用 |
| 带宽/多线 | SQM、EQoS、MWAN3、MWAN3 Helper、syncdial、nlbwmon、wrtbwmon、Netdata | 未选中这些管理插件；TurboACC 仍启用 |
| 其他 | DDNS、UPnP、WOL、打印机、推送、游戏加速、解锁音乐等对应插件；coremark、cpufreq、autosamba 等 | 根据配置显式关闭，最终仍需检查依赖是否重新选择 |

### 去哪里核对一次构建的完整清单

两个编译工作流现在都会生成并上传：

- `build-packages.txt`：`make defconfig` 后实际选择的软件包名，包含自动依赖；`y` 表示选入固件，
  `m` 表示只构建软件包。此清单通过包元数据过滤，不会把 `*_INCLUDE_*` 之类功能开关误当作包名。
- `build.config`：当次完整解析配置，可核对插件子选项和内核设置。
- `*.manifest`：生成固件中实际安装的包及版本；核对最终固件时以它为准。
- `passwall-versions.txt`：两个插件的源码提交、来源和固件版本检查结果。

Artifact 的 `bin` 中保存上述配置与清单；Release 也会附带它们。
编译失败时不保证生成固件 manifest；这里的分析不是一次已经完成编译的完整包清单。

### 不执行固件编译的工作流

| 工作流 | 功能 | 备注 |
| --- | --- | --- |
| Cache-Clean | 删除仓库 Actions 缓存 | 不编译固件；之后运行可能需要重建工具链 |
| Delete Old Workflows | 清理旧任务记录及旧 Release/tag | 保留策略是任务记录 2 天、Release 最新 15 个；不编译固件 |

四个工作流当前都由 `workflow_dispatch` 手动触发，定时任务行处于注释状态。
