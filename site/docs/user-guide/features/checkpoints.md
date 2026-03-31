# 文件系统检查点

Hermes 会在修改文件前自动为工作目录创建快照，为你提供安全网，以便在出现问题时回滚。检查点**默认启用**。

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `/rollback` | 列出所有检查点及其变更统计信息 |
| `/rollback <N>` | 恢复到检查点 N（同时撤销上一次聊天回合） |
| `/rollback diff <N>` | 预览检查点 N 与当前状态之间的差异 |
| `/rollback <N> <file>` | 从检查点 N 恢复单个文件 |

## 触发检查点的操作

- **文件工具** — `write_file` 和 `patch`
- **破坏性终端命令** — `rm`、`mv`、`sed -i`、输出重定向 (`>`)、`git reset`/`clean`

## 配置

```yaml
# ~/.hermes/config.yaml
checkpoints:
  enabled: true          # 默认值: true
  max_snapshots: 50      # 每个目录的最大检查点数量
```

## 了解更多

完整指南 — 包括影子仓库的工作原理、差异预览、文件级恢复、对话撤销、安全防护和最佳实践 — 请参阅 **[检查点与 /rollback](../checkpoints-and-rollback.md)**。
