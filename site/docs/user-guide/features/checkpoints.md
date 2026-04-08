# 文件系统 Checkpoints

Hermes 会在修改文件前自动对你的工作目录进行快照（snapshot），为你提供一个安全网，以便在出现问题时进行回滚。Checkpoints 功能**默认开启**。

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `/rollback` | 列出所有 Checkpoints 及其变更统计 |
| `/rollback <N>` | 恢复到 Checkpoint N（同时撤销上一次对话轮次） |
| `/rollback diff <N>` | 预览 Checkpoint N 与当前状态之间的差异（diff） |
| `/rollback <N> <file>` | 从 Checkpoint N 中恢复单个文件 |

## 触发 Checkpoints 的操作

- **文件工具** — `write_file` 和 `patch`
- **破坏性终端命令** — `rm`、`mv`、`sed -i`、输出重定向 (`>`)、`git reset`/`clean`

## 配置

```yaml
# ~/.hermes/config.yaml
checkpoints:
  enabled: true          # 默认值: true
  max_snapshots: 50      # 每个目录保留的最大 Checkpoints 数量
```

## 了解更多

关于完整指南 —— 包括 shadow repos 的工作原理、diff 预览、文件级恢复、对话撤销、安全防护以及最佳实践 —— 请参阅 **[Checkpoints 与 /rollback](../checkpoints-and-rollback.md)**。
