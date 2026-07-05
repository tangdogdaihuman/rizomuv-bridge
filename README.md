# RizomUV Bridge

JSON-over-Python bridge to control [RizomUV Standalone](https://rizom-lab.com) from any tool that can call `python` with a JSON argument.

Wraps the official [RizomUVLink](https://github.com/Rizom-Lab/RizomUVLink) module with a simple JSON IPC interface, so you can drive RizomUV from shell scripts, CI pipelines, or LLM agents.

## Requirements

- **RizomUV Standalone** 2022.2 or later (purchased license)
- **Python** 3.6–3.12 (matching your RizomUV installation)

## Quick Start

```powershell
# 1. Start RizomUV
python rizomuv_bridge.py '{"op": "run"}'

# 2. Load a mesh
python rizomuv_bridge.py '{"op": "load", "params": {"File.Path": "model.obj", "File.XYZUVW": true}}'

# 3. Pack UVs
python rizomuv_bridge.py '{"op": "pack", "params": {"Translate": true}}'

# 4. Save
python rizomuv_bridge.py '{"op": "save", "params": {"File.Path": "output.obj"}}'

# 5. Quit
python rizomuv_bridge.py '{"op": "quit"}'
```

## Available Operations

| Op | Description |
|---|---|
| `run` | Start RizomUV and connect (or reconnect to existing instance) |
| `load` | Load mesh from file |
| `unfold` | Unfold UV islands |
| `pack` | Pack UV islands |
| `save` | Save mesh to file |
| `cut` | Cut mesh edges for UV unwrapping |
| `weld` | Weld vertices/edges |
| `select` | Select elements (islands, edges, vertices) |
| `optimize` | Optimize UV layout |
| `island_groups` | Get/set island groups |
| `island_properties` | Get/set island properties |
| `tag` | Tag elements |
| `hotspot` | Hotspot operations |
| `uvset` | UV set operations |
| `deform` | Deform operations |
| `raster_export` | Export UV raster image |
| `get` | Read RizomUV variables |
| `set` | Set RizomUV variables |
| `execute` | Execute any RizomUV API command directly |
| `quit` | Close RizomUV |

## License

- `rizomuv_bridge.py` — MIT
- `RizomUVLink/` — MIT (Copyright Rizom-Lab)
