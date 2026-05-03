---
sidebar_position: 8
title: "扩展 CLI"
description: "构建包装 CLI，通过自定义组件、快捷键和布局变更来扩展 Hermes TUI"
---

# 扩展 CLI {#extending-the-cli}

Hermes 在 `HermesCLI` 上暴露了受保护的扩展钩子，这样包装 CLI 就可以添加组件、快捷键和布局自定义，而无需重写那 1000 多行的 `run()` 方法。这能让你的扩展与内部变更解耦。

## 扩展点 {#extension-points}

共有五个可用的扩展接口：

| 钩子 | 用途 | 何时重写 |
|------|---------|------------------|
| `_get_extra_tui_widgets()` | 向布局中注入组件 | 你需要一个持久的 UI 元素（面板、状态栏、迷你播放器） |
| `_register_extra_tui_keybindings(kb, *, input_area)` | 添加快捷键 | 你需要热键（切换面板、传输控制、模态快捷键） |
| `_build_tui_layout_children(**widgets)` | 完全控制组件顺序 | 你需要重新排序或包装现有组件（很少用） |
| `process_command()` | 添加自定义斜杠命令 | 你需要处理 `/mycommand`（已有钩子） |
| `_build_tui_style_dict()` | 自定义 prompt_toolkit 样式 | 你需要自定义颜色或样式（已有钩子） |

前三个是新增的受保护钩子。后两个已经存在。

## 快速开始：一个包装 CLI {#quick-start-a-wrapper-cli}

```python
#!/usr/bin/env python3
"""my_cli.py — 一个扩展 Hermes 的包装 CLI 示例。"""

from cli import HermesCLI
from prompt_toolkit.layout import FormattedTextControl, Window
from prompt_toolkit.filters import Condition


class MyCLI(HermesCLI):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._panel_visible = False

    def _get_extra_tui_widgets(self):
        """在状态栏上方添加一个可切换的信息面板。"""
        cli_ref = self
        return [
            Window(
                FormattedTextControl(lambda: "📊 我的自定义面板内容"),
                height=1,
                filter=Condition(lambda: cli_ref._panel_visible),
            ),
        ]

    def _register_extra_tui_keybindings(self, kb, *, input_area):
        """F2 切换自定义面板。"""
        cli_ref = self

        @kb.add("f2")
        def _toggle_panel(event):
            cli_ref._panel_visible = not cli_ref._panel_visible

    def process_command(self, cmd: str) -> bool:
        """添加一个 /panel 斜杠命令。"""
        if cmd.strip().lower() == "/panel":
            self._panel_visible = not self._panel_visible
            state = "可见" if self._panel_visible else "隐藏"
            print(f"面板现在 {state}")
            return True
        return super().process_command(cmd)


if __name__ == "__main__":
    cli = MyCLI()
    cli.run()
```

运行它：

```bash
cd ~/.hermes/hermes-agent
source .venv/bin/activate
python my_cli.py
```

## 钩子参考 {#hook-reference}

### `_get_extra_tui_widgets()` {#getextratuiwidgets}

返回一个 prompt_toolkit 组件列表，用于插入到 TUI 布局中。组件会出现在**间隔条和状态栏之间**——在输入区域之上但主输出区域之下。

```python
def _get_extra_tui_widgets(self) -> list:
    return []  # 默认：没有额外组件
```

每个组件应该是一个 prompt_toolkit 容器（例如 `Window`、`ConditionalContainer`、`HSplit`）。使用 `ConditionalContainer` 或 `filter=Condition(...)` 来让组件可切换。
```python
from prompt_toolkit.layout import ConditionalContainer, Window, FormattedTextControl
from prompt_toolkit.filters import Condition

def _get_extra_tui_widgets(self):
    return [
        ConditionalContainer(
            Window(FormattedTextControl("Status: connected"), height=1),
            filter=Condition(lambda: self._show_status),
        ),
    ]
```

### `_register_extra_tui_keybindings(kb, *, input_area)` {#registerextratuikeybindings-kb-inputarea}

在 Hermes 注册自己的按键绑定之后、布局构建之前调用。将你的按键绑定添加到 `kb` 中。

```python
def _register_extra_tui_keybindings(self, kb, *, input_area):
    pass  # 默认：无额外按键绑定
```

参数：
- **`kb`** — prompt_toolkit 应用的 `KeyBindings` 实例
- **`input_area`** — 主 `TextArea` 控件，如果你需要读取或操作用户输入

```python
def _register_extra_tui_keybindings(self, kb, *, input_area):
    cli_ref = self

    @kb.add("f3")
    def _clear_input(event):
        input_area.text = ""

    @kb.add("f4")
    def _insert_template(event):
        input_area.text = "/search "
```

**避免与内置按键绑定冲突**：`Enter`（提交）、`Escape Enter`（换行）、`Ctrl-C`（中断）、`Ctrl-D`（退出）、`Tab`（自动建议接受）。功能键 F2 及以上、Ctrl 组合键通常是安全的。

### `_build_tui_layout_children(**widgets)` {#buildtuilayoutchildren-widgets}

仅当你需要完全控制控件顺序时才重写此方法。大多数扩展应使用 `_get_extra_tui_widgets()` 代替。

```python
def _build_tui_layout_children(self, *, sudo_widget, secret_widget,
    approval_widget, clarify_widget, model_picker_widget=None,
    spinner_widget=None, spacer, status_bar, input_rule_top,
    image_bar, input_area, input_rule_bot, voice_status_bar,
    completions_menu) -> list:
```

默认实现返回（任何 `None` 的控件会被过滤掉）：

```python
[
    Window(height=0),       # 锚点
    sudo_widget,            # sudo 密码提示（条件性）
    secret_widget,          # 密钥输入提示（条件性）
    approval_widget,        # 危险命令审批（条件性）
    clarify_widget,         # 澄清问题 UI（条件性）
    model_picker_widget,    # 模型选择器覆盖层（条件性）
    spinner_widget,         # 思考中旋转器（条件性）
    spacer,                 # 填充剩余垂直空间
    *self._get_extra_tui_widgets(),  # 你的控件放在这里
    status_bar,             # 模型/令牌/上下文状态行
    input_rule_top,         # ─── 输入框上方边框
    image_bar,              # 已附加图片指示器
    input_area,             # 用户文本输入
    input_rule_bot,         # ─── 输入框下方边框
    voice_status_bar,       # 语音模式状态（条件性）
    completions_menu,       # 自动补全下拉菜单
]
```

## 布局示意图 {#layout-diagram}

默认布局从上到下：

1. **输出区域** — 滚动对话历史
2. **间隔器**
3. **额外控件** — 来自 `_get_extra_tui_widgets()`
4. **状态栏** — 模型、上下文百分比、已用时间
5. **图片栏** — 已附加图片数量
6. **输入区域** — 用户提示
7. **语音状态** — 录音指示器
8. **补全菜单** — 自动补全建议
## 提示 {#tips}

- **状态变更后刷新显示**：调用 `self._invalidate()` 触发 prompt_toolkit 重绘。
- **访问 Agent 状态**：`self.agent`、`self.model`、`self.conversation_history` 均可直接使用。
- **自定义样式**：重写 `_build_tui_style_dict()` 方法，为你的自定义样式类添加条目。
- **斜杠命令**：重写 `process_command()` 方法，处理你的命令，其余情况调用 `super().process_command(cmd)`。
- **除非绝对必要，不要重写 `run()`**——扩展钩子正是为了避免这种耦合而设计的。
