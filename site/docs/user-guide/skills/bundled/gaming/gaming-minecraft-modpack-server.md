---
title: "Minecraft Modpack Server — 搭建模组版 Minecraft 服务器（CurseForge、Modrinth）"
sidebar_label: "Minecraft Modpack Server"
description: "搭建模组版 Minecraft 服务器（CurseForge、Modrinth）"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Minecraft Modpack Server {#minecraft-modpack-server}

搭建模组版 Minecraft 服务器（CurseForge、Modrinth）。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 内置（默认安装） |
| 路径 | `skills/gaming/minecraft-modpack-server` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Minecraft Modpack Server 搭建指南 {#minecraft-modpack-server-setup}

## 何时使用 {#when-to-use}
- 用户想通过服务器整合包 zip 文件搭建模组版 Minecraft 服务器
- 用户需要 NeoForge/Forge 服务器配置方面的帮助
- 用户询问 Minecraft 服务器性能调优或备份相关的问题

## 先收集用户偏好 {#gather-user-preferences-first}
在开始搭建之前，询问用户以下信息：
- **服务器名称 / MOTD** — 服务器列表中应显示什么内容？
- **种子** — 指定种子还是随机生成？
- **难度** — 和平 / 简单 / 普通 / 困难？
- **游戏模式** — 生存 / 创造 / 冒险？
- **在线模式** — true（Mojang 认证，正版账户）或 false（局域网/离线友好）？
- **玩家数量** — 预计有多少玩家？（影响内存和视距调优）
- **内存分配** — 由用户指定，还是让 Agent 根据模组数量和可用内存决定？
- **视距 / 模拟距离** — 由用户指定，还是让 Agent 根据玩家数量和硬件选择？
- **PvP** — 开启还是关闭？
- **白名单** — 开放服务器还是仅限白名单？
- **备份** — 需要自动备份吗？多久备份一次？

如果用户不在意，使用合理的默认值，但在生成配置前务必询问。

## 步骤 {#steps}

### 1. 下载并检查整合包 {#1-download-inspect-the-pack}
```bash
mkdir -p ~/minecraft-server
cd ~/minecraft-server
wget -O serverpack.zip "<URL>"
unzip -o serverpack.zip -d server
ls server/
```
查找以下内容：`startserver.sh`、安装程序 jar 包（neoforge/forge）、`user_jvm_args.txt`、`mods/` 文件夹。
检查脚本以确定：模组加载器类型、版本以及所需的 Java 版本。

### 2. 安装 Java {#2-install-java}
- Minecraft 1.21+ → Java 21：`sudo apt install openjdk-21-jre-headless`
- Minecraft 1.18-1.20 → Java 17：`sudo apt install openjdk-17-jre-headless`
- Minecraft 1.16 及以下 → Java 8：`sudo apt install openjdk-8-jre-headless`
- 验证：`java -version`

### 3. 安装模组加载器 {#3-install-the-mod-loader}
大多数服务器整合包都包含安装脚本。使用 INSTALL_ONLY 环境变量进行安装而不启动服务器：
```bash
cd ~/minecraft-server/server
ATM10_INSTALL_ONLY=true bash startserver.sh
# 或者对于通用 Forge 整合包：
# java -jar forge-*-installer.jar --installServer
```
这会下载库文件、修补服务器 jar 包等。

### 4. 接受 EULA {#4-accept-eula}
```bash
echo "eula=true" > ~/minecraft-server/server/eula.txt
```

### 5. 配置 server.properties {#5-configure-server-properties}
模组版/局域网的关键设置：
```properties
motd=\u00a7b\u00a7l服务器名称 \u00a7r\u00a78| \u00a7a模组包名称
server-port=25565
online-mode=true          # 局域网无 Mojang 认证时设为 false
enforce-secure-profile=true  # 与 online-mode 保持一致
difficulty=hard            # 大多数模组包以困难模式平衡
allow-flight=true          # 模组版必须开启（飞行坐骑/物品）
spawn-protection=0         # 允许所有人在出生点建造
max-tick-time=180000       # 模组版需要更长的 tick 超时时间
enable-command-block=true
```
性能设置（根据硬件调整）：
```properties
# 2 名玩家，高性能机器：
view-distance=16
simulation-distance=10

# 4-6 名玩家，中等性能机器：
view-distance=10
simulation-distance=6

# 8 名以上玩家或性能较弱的硬件：
view-distance=8
simulation-distance=4
```

### 6. 调整 JVM 参数（user_jvm_args.txt） {#6-tune-jvm-args-userjvmargs-txt}
根据玩家数量和模组数量调整内存。模组服的经验法则：
- 100-200 个模组：6-12GB
- 200-350+ 个模组：12-24GB
- 至少为操作系统/其他任务预留 8GB 内存

```
-Xms12G
-Xmx24G
-XX:+UseG1GC
-XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:+DisableExplicitGC
-XX:+AlwaysPreTouch
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:G1HeapRegionSize=8M
-XX:G1ReservePercent=20
-XX:G1HeapWastePercent=5
-XX:G1MixedGCCountTarget=4
-XX:InitiatingHeapOccupancyPercent=15
-XX:G1MixedGCLiveThresholdPercent=90
-XX:G1RSetUpdatingPauseTimePercent=5
-XX:SurvivorRatio=32
-XX:+PerfDisableSharedMem
-XX:MaxTenuringThreshold=1
```

### 7. 开放防火墙 {#7-open-firewall}
```bash
sudo ufw allow 25565/tcp comment "Minecraft Server"
```
检查命令：`sudo ufw status | grep 25565`

### 8. 创建启动脚本 {#8-create-launch-script}
```bash
cat > ~/start-minecraft.sh << 'EOF'
#!/bin/bash
cd ~/minecraft-server/server
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/<VERSION>/unix_args.txt nogui
EOF
chmod +x ~/start-minecraft.sh
```
注意：对于 Forge（而非 NeoForge），参数文件路径不同。请查看 `startserver.sh` 以获取确切路径。

### 9. 设置自动备份 {#9-set-up-automated-backups}
创建备份脚本：
```bash
cat > ~/minecraft-server/backup.sh << 'SCRIPT'
#!/bin/bash
SERVER_DIR="$HOME/minecraft-server/server"
BACKUP_DIR="$HOME/minecraft-server/backups"
WORLD_DIR="$SERVER_DIR/world"
MAX_BACKUPS=24
mkdir -p "$BACKUP_DIR"
[ ! -d "$WORLD_DIR" ] && echo "[BACKUP] No world folder" && exit 0
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/world_${TIMESTAMP}.tar.gz"
echo "[BACKUP] Starting at $(date)"
tar -czf "$BACKUP_FILE" -C "$SERVER_DIR" world
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[BACKUP] Saved: $BACKUP_FILE ($SIZE)"
BACKUP_COUNT=$(ls -1t "$BACKUP_DIR"/world_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    REMOVE=$((BACKUP_COUNT - MAX_BACKUPS))
    ls -1t "$BACKUP_DIR"/world_*.tar.gz | tail -n "$REMOVE" | xargs rm -f
    echo "[BACKUP] Pruned $REMOVE old backup(s)"
fi
echo "[BACKUP] Done at $(date)"
SCRIPT
chmod +x ~/minecraft-server/backup.sh
```

添加每小时定时任务：
```bash
(crontab -l 2>/dev/null | grep -v "minecraft/backup.sh"; echo "0 * * * * $HOME/minecraft-server/backup.sh >> $HOME/minecraft-server/backups/backup.log 2>&1") | crontab -
```

## 常见陷阱 {#pitfalls}
- 模组服**务必**设置 `allow-flight=true`——否则使用喷气背包/飞行模组的玩家会被踢出
- `max-tick-time=180000` 或更高——模组服在生成世界时经常出现长 tick
- 首次启动**非常慢**（大型整合包需要几分钟）——别慌
- 首次启动时出现 "Can't keep up!" 警告是正常的，初始区块生成后会稳定下来
- 如果 `online-mode=false`，也要设置 `enforce-secure-profile=false`，否则客户端会被拒绝连接
- 整合包的 startserver.sh 通常带有自动重启循环——建议创建一个干净的启动脚本，不要包含这个循环
- 删除 world/ 文件夹可以用新种子重新生成世界
- 有些整合包通过环境变量控制行为（例如 ATM10 使用 ATM10_JAVA、ATM10_RESTART、ATM10_INSTALL_ONLY）
## 验证 {#verification}
- 使用 `pgrep -fa neoforge` 或 `pgrep -fa minecraft` 检查是否正在运行
- 查看日志：`tail -f ~/minecraft-server/server/logs/latest.log`
- 在日志中查找 "Done (Xs)!" 字样 = 服务器已就绪
- 测试连接：玩家在多人游戏中添加服务器 IP
