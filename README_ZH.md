# RizomUV Bridge

通过 JSON 命令行驱动 [RizomUV Standalone](https://rizom-lab.com) 的桥接工具。

底层封装了 RizomUV 官方的 [RizomUVLink](https://github.com/Rizom-Lab/RizomUVLink) 模块，对外暴露 JSON IPC 接口。可以用脚本、CI 流水线、LLM agent 控制 RizomUV。

## 环境要求

- **RizomUV Standalone** 2022.2 或更高版本（需购买授权）
- **Python** 3.6–3.12（需与 RizomUV 自带的 Python 版本匹配）

## 快速上手

```powershell
# 1. 启动 RizomUV
python rizomuv_bridge.py '{"op": "run"}'

# 2. 加载模型
python rizomuv_bridge.py '{"op": "load", "params": {"File.Path": "model.obj", "File.XYZUVW": true}}'

# 3. UV 展开
python rizomuv_bridge.py '{"op": "unfold", "params": {}}'

# 4. UV 打包
python rizomuv_bridge.py '{"op": "pack", "params": {"Translate": true}}'

# 5. 保存
python rizomuv_bridge.py '{"op": "save", "params": {"File.Path": "output.obj"}}'

# 6. 退出
python rizomuv_bridge.py '{"op": "quit"}'
```

## 支持的操作

| 操作 | 说明 |
|---|---|
| `run` | 启动 RizomUV 并建立连接（也可重连已运行的实例） |
| `load` | 从文件加载模型 |
| `unfold` | UV 展开 |
| `pack` | UV 打包 |
| `save` | 保存模型到文件 |
| `cut` | 切割边（用于 UV 展开） |
| `weld` | 焊接顶点/边 |
| `select` | 选择元素（UV 岛、边、顶点） |
| `optimize` | UV 布局优化 |
| `island_groups` | 获取/设置 UV 岛分组 |
| `island_properties` | 获取/设置 UV 岛属性 |
| `tag` | 标签操作 |
| `hotspot` | Hotspot 操作 |
| `uvset` | UV 通道操作 |
| `deform` | 变形操作 |
| `raster_export` | 导出 UV 栅格图像 |
| `get` | 读取 RizomUV 变量 |
| `set` | 设置 RizomUV 变量 |
| `execute` | 直接执行任意 RizomUV API 命令 |
| `quit` | 关闭 RizomUV |

## 通信方式

每次调用 `python rizomuv_bridge.py '<json>'` 都会启动一个独立的 Python 进程。

首次调用 `run` 会启动 RizomUV 并记录端口到临时文件。后续调用会自动重连到已有的 RizomUV 实例，无需保持长连接。

## 参数格式

`load`、`pack` 等操作的参数直接透传到 RizomUV API，具体参数见 [RizomUV 脚本参考文档](https://docs.rizom-lab.com/rizomuv/)。

## 许可证

- `rizomuv_bridge.py` — MIT
- `RizomUVLink/` — MIT（Copyright Rizom-Lab）
