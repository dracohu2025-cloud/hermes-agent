---
title: "Canvas — Canvas LMS 集成 — 使用 API 令牌认证获取已注册课程和作业"
sidebar_label: "Canvas"
description: "Canvas LMS 集成 — 使用 API 令牌认证获取已注册课程和作业"
---

{/* 此页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请编辑源文件 SKILL.md，而非此页面。 */}

# Canvas {#canvas}

Canvas LMS 集成 — 使用 API 令牌认证获取已注册课程和作业。

## 技能元数据 {#skill-metadata}

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/productivity/canvas` 安装 |
| 路径 | `optional-skills/productivity/canvas` |
| 版本 | `1.0.0` |
| 作者 | 社区 |
| 许可证 | MIT |
| 标签 | `Canvas`, `LMS`, `Education`, `Courses`, `Assignments` |

## 参考：完整 SKILL.md {#reference-full-skill-md}

:::info
以下是 Hermes 在触发此技能时加载的完整技能定义。这是 Agent 在技能激活时看到的指令。
:::

# Canvas LMS — 课程与作业访问 {#canvas-lms-course-assignment-access}

对 Canvas LMS 的只读访问，用于列出课程和作业。

## 脚本 {#scripts}

- `scripts/canvas_api.py` — 用于 Canvas API 调用的 Python CLI

## 设置 {#setup}

1. 在浏览器中登录你的 Canvas 实例
2. 进入 **账户 → 设置**（点击你的个人资料图标，然后选择设置）
3. 滚动到 **已批准的集成**，点击 **+ 新建访问令牌**
4. 为令牌命名（例如 "Hermes Agent"），设置可选的过期时间，然后点击 **生成令牌**
5. 复制令牌并添加到 `~/.hermes/.env`：

```
CANVAS_API_TOKEN=你的令牌
CANVAS_BASE_URL=https://你的学校.instructure.com
```

基础 URL 就是你登录 Canvas 时浏览器中显示的地址（末尾不要带斜杠）。

## 用法 {#usage}

```bash
CANVAS="python $HERMES_HOME/skills/productivity/canvas/scripts/canvas_api.py"

# 列出所有活跃课程
$CANVAS list_courses --enrollment-state active

# 列出所有课程（任何状态）
$CANVAS list_courses

# 列出特定课程的作业
$CANVAS list_assignments 12345

# 按截止日期排序列出作业
$CANVAS list_assignments 12345 --order-by due_at
```

## 输出格式 {#output-format}

**list_courses** 返回：
```json
[{"id": 12345, "name": "Intro to CS", "course_code": "CS101", "workflow_state": "available", "start_at": "...", "end_at": "..."}]
```

**list_assignments** 返回：
```json
[{"id": 67890, "name": "Homework 1", "due_at": "2025-02-15T23:59:00Z", "points_possible": 100, "submission_types": ["online_upload"], "html_url": "...", "description": "...", "course_id": 12345}]
```

注意：作业描述会被截断为 500 个字符。`html_url` 字段链接到 Canvas 中的完整作业页面。

## API 参考（curl） {#api-reference-curl}

```bash
# 列出课程
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_BASE_URL/api/v1/courses?enrollment_state=active&per_page=10"

# 列出课程的作业
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_BASE_URL/api/v1/courses/COURSE_ID/assignments?per_page=10&order_by=due_at"
```

Canvas 使用 `Link` 头进行分页。Python 脚本会自动处理分页。

## 规则 {#rules}

- 此技能为**只读** — 仅获取数据，绝不修改课程或作业
- 首次使用时，通过运行 `$CANVAS list_courses` 验证认证 — 如果返回 401 错误，引导用户完成设置
- Canvas 的速率限制约为每 10 分钟 700 次请求；如果遇到限制，请检查 `X-Rate-Limit-Remaining` 头
## 故障排除 {#troubleshooting}

| 问题 | 解决方法 |
|---------|-----|
| 401 Unauthorized | Token 无效或已过期 — 在 Canvas 设置中重新生成 |
| 403 Forbidden | Token 缺少该课程的权限 |
| 课程列表为空 | 尝试 `--enrollment-state active` 或省略该标志以查看所有状态 |
| 机构错误 | 确认 `CANVAS_BASE_URL` 与浏览器中的 URL 一致 |
| 超时错误 | 检查到 Canvas 实例的网络连接 |
