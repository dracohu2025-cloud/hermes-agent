---
title: "Blender Mcp — 通过 Socket 连接 blender-mcp 插件，直接从 Hermes 控制 Blender"
sidebar_label: "Blender Mcp"
description: "通过 Socket 连接 blender-mcp 插件，直接从 Hermes 控制 Blender"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

<a id="blender-mcp"></a>
# Blender Mcp

通过 Socket 连接 blender-mcp 插件，直接从 Hermes 控制 Blender。创建 3D 对象、材质、动画，以及运行任意 Blender Python (bpy) 代码。当用户希望在 Blender 中创建或修改任何内容时使用。

<a id="skill-metadata"></a>
## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/creative/blender-mcp` 安装 |
| 路径 | `optional-skills/creative/blender-mcp` |
| 版本 | `1.0.0` |
| 作者 | alireza78a |
| 平台 | linux, macos, windows |

<a id="reference-full-skill-md"></a>
## 参考：完整的 SKILL.md

:::info
以下是该技能被触发时 Hermes 加载的完整技能定义。这是技能激活时 Agent 看到的指令。
:::

# Blender MCP

通过 TCP 端口 9876 上的 Socket，从 Hermes 控制正在运行的 Blender 实例。

<a id="setup-one-time"></a>
## 设置（一次性）

<a id="1-install-the-blender-addon"></a>
### 1. 安装 Blender 插件

    curl -sL https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py -o ~/Desktop/blender_mcp_addon.py

In Blender:
    Edit > Preferences > Add-ons > Install > select blender_mcp_addon.py
    Enable "Interface: Blender MCP"

<a id="2-start-the-socket-server-in-blender"></a>
### 2. 在 Blender 中启动 Socket 服务器

Press N in Blender viewport to open sidebar.
Find "BlenderMCP" tab and click "Start Server".

<a id="3-verify-connection"></a>
### 3. 验证连接

    nc -z -w2 localhost 9876 && echo "OPEN" || echo "CLOSED"

<a id="protocol"></a>
## 协议

通过 TCP 传输纯 UTF-8 JSON——没有长度前缀。

发送：    &#123;"type": "&lt;command>", "params": &#123;&lt;kwargs>&#125;&#125;
接收：    &#123;"status": "success", "result": &lt;value>&#125;
          &#123;"status": "error",   "message": "&lt;reason>"&#125;

<a id="available-commands"></a>
## 可用命令

| 类型                    | 参数             | 描述                               |
|-------------------------|------------------|------------------------------------|
| execute_code            | code (str)       | 运行任意 bpy Python 代码           |
| get_scene_info          | (none)           | 列出场景中所有对象                 |
| get_object_info         | object_name (str)| 获取特定对象的详细信息             |
| get_viewport_screenshot | (none)           | 当前视口的截图                     |

<a id="python-helper"></a>
## Python 辅助函数

在 execute_code 工具调用中使用此函数：

    import socket, json

    def blender_exec(code: str, host="localhost", port=9876, timeout=15):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(timeout)
        payload = json.dumps(&#123;"type": "execute_code", "params": &#123;"code": code&#125;&#125;)
        s.sendall(payload.encode("utf-8"))
        buf = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                try:
                    json.loads(buf.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    continue
            except socket.timeout:
                break
        s.close()
        return json.loads(buf.decode("utf-8"))
<a id="common-bpy-patterns"></a>
## 常见 bpy 模式

<a id="clear-scene"></a>
### 清空场景
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

<a id="add-mesh-objects"></a>
### 添加网格物体
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 0))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(-3, 0, 0))

<a id="create-and-assign-material"></a>
### 创建并分配材质
    mat = bpy.data.materials.new(name="MyMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (R, G, B, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Metallic"].default_value = 0.0
    obj.data.materials.append(mat)

<a id="keyframe-animation"></a>
### 关键帧动画
    obj.location = (0, 0, 0)
    obj.keyframe_insert(data_path="location", frame=1)
    obj.location = (0, 0, 3)
    obj.keyframe_insert(data_path="location", frame=60)

<a id="render-to-file"></a>
### 渲染到文件
    bpy.context.scene.render.filepath = "/tmp/render.png"
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

<a id="pitfalls"></a>
## 注意事项

- 运行前必须检查套接字是否打开（`nc -z localhost 9876`）
- 每个 Blender 会话都需在内部启动 Addon 服务器（N-panel > BlenderMCP > Connect）
- 将复杂场景拆分为多个较小的 `execute_code` 调用，避免超时
- 渲染输出路径必须是绝对路径（`/tmp/...`），不能使用相对路径
- `shade_smooth()` 要求物体处于选中状态且处于物体模式
