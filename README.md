## 特别提示 [![](https://img.shields.io/badge/-个人免责声明-FFFFFF.svg)](#特别提示-)

- **本人不对任何人因使用本固件所遭受的任何理论或实际的损失承担责任！**

- **本固件禁止用于任何商业用途，请务必严格遵守国家互联网使用相关法律规定！**

## 项目说明 [![](https://img.shields.io/badge/-项目基本介绍-FFFFFF.svg)](#项目说明-)
- 固件默认管理地址：`192.168.8.1` 默认用户：`root` 默认密码：`password`

## PassWall 固定版本编译

X86-64 和 NanoPi-R3S 工作流均使用以下源码版本：

| 软件包 | 版本 / 上游 tag | 固定 commit |
| --- | --- | --- |
| luci-app-passwall | 26.1.13-1 | 1f589523b33bd312b9cf38394c72493e0fde64ea |
| luci-app-passwall2 | 25.11.18-1 | dbf48fb5bd9f6e68824800cf418265b42c943c7d |

原配置虽然指定了 tag，但 `luci` feed 也提供同名包，且位于它们之前。
`feeds install -a` 会优先使用先安装的同名包，因此不能仅凭拉取了 tag 判断实际编译版本。

现在使用 `URL^commit` 固定源码，并将这两个 feed 放在 `luci` 前面；工作流先卸载旧链接，
再用 `install -f -p` 安装指定来源，最后安装其余 feeds。工具链缓存也使用新的命名空间，
并包含 feeds、版本检查脚本和设备配置的哈希。

编译前检查实际源码链接、commit、Makefile 版本和 `.config` 的 `=y` 选择；编译后检查每个固件
manifest 内的实际安装版本和生成的 IPK 文件版本。任何检查失败都会停止，禁止上传或发布。
成功时 Actions 摘要及固件附件 `passwall-versions.txt` 会记录版本和源码提交。
新版 `luci.mk` 可能将包版本写为 `26.1.13-r1` / `25.11.18-r1`；
`r1` 与 `1` 均表示上游的第 1 次打包，检查允许这两种格式，其他版本或 release 均不允许。

使用方法：打开 **Actions → X86-64 或 NanoPi-R3S → Run workflow**，
在分支下拉框选择 **fix/pin-passwall-versions** 后运行。不要选择 `main` 或重跑旧提交的任务。
Release tag 将指向本次工作流实际使用的提交。

以后升级时，同时更新 `feeds.conf.default` 中的 commit 和 `scripts/check-passwall.py` 中的
`LOCKS`，核对上游 Makefile 的 `PKG_VERSION`、`PKG_RELEASE` 后重新编译。
这里锁定的是两个 LuCI 插件版本；代理核心和其他依赖仍由现有 feeds 提供，未锁定整个固件依赖树。
