#!/usr/bin/env python3
"""
RizomUV Bridge - JSON-based IPC to control RizomUV Standalone
Called as: python rizomuv_bridge.py <json_command>
Returns JSON to stdout.

Usage:
    python rizomuv_bridge.py '{"op": "run"}'
    python rizomuv_bridge.py '{"op": "load", "params": {"File.Path": "mesh.obj"}}'
    python rizomuv_bridge.py '{"op": "unfold", "params": {}}'
    python rizomuv_bridge.py '{"op": "pack", "params": {"Translate": true}}'
    python rizomuv_bridge.py '{"op": "save", "params": {"File.Path": "out.obj"}}'
    python rizomuv_bridge.py '{"op": "quit"}'
"""

import sys
import os
import json
import subprocess
import time
import socket

# Add RizomUVLink to path
RIZOM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RIZOM_DIR, "RizomUVLink"))

from RizomUVLink import CRizomUVLink
from RizomUVLinkBase import CZEx

# ---- Port management ----

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        return s.connect_ex(('127.0.0.1', port)) == 0

# ---- Global state ----

link = None
rizom_process = None
PORT_FILE = os.path.join(os.environ.get('TEMP', '.'), 'rizomuv_bridge_port.json')

def save_port(port):
    with open(PORT_FILE, 'w') as f:
        json.dump({"port": port}, f)

def load_port():
    try:
        with open(PORT_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

# ---- Reconnect ----

def _try_reconnect():
    """Try to reconnect to an existing RizomUV instance from a previous bridge call."""
    global link
    port_data = load_port()
    if not port_data:
        return False
    if not is_port_open(port_data["port"]):
        return False
    try:
        link = CRizomUVLink()
        link.Connect(port_data["port"])
        ver = link.rizomuv.Execute('Get', 'Vars.Infos.Version.Full', 10000)
        if ver:
            return True
    except Exception:
        pass
    link = None
    return False

def _ensure_connected():
    if link is not None:
        return None
    if _try_reconnect():
        return None
    return {"ok": False, "error": "Not connected. Call run first."}

# ---- Core operations ----

def cmd_run(params):
    """Start RizomUV and connect."""
    global link, rizom_process

    if link is not None:
        return {"ok": True, "msg": "Already connected", "port": link.port}

    # Try reconnect to existing instance
    if _try_reconnect():
        return {"ok": True, "msg": "Reconnected to existing RizomUV", "port": link.port}

    # Start new instance
    port = params.get("port") or find_free_port()
    exe_path = os.path.join(RIZOM_DIR, "rizomuv.exe")

    if not os.path.exists(exe_path):
        return {"ok": False, "error": f"RizomUV not found at {exe_path}"}

    # Launch with /nle (no license exit - exit with error if no license)
    proc = subprocess.Popen(
        [exe_path, f"/id{port}", "/nle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS if sys.platform == 'win32' else 0
    )
    rizom_process = proc
    save_port(port)

    # RizomUV needs ~10s to initialize its scripting API server
    time.sleep(10)

    # Create link and connect
    link = CRizomUVLink()
    link.Connect(port)

    # Poll for API readiness (up to ~3 min)
    for attempt in range(36):
        try:
            ver = link.rizomuv.Execute('Get', 'Vars.Infos.Version.Full', 10000)
            if ver:
                return {"ok": True, "msg": f"Started RizomUV {ver}", "port": port, "pid": proc.pid}
        except Exception:
            pass
        time.sleep(5)

    return {"ok": False, "error": "RizomUV started but API server did not respond within 3 min"}


def cmd_load(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Load(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_unfold(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Unfold(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_pack(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Pack(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_save(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Save(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_quit(params):
    global link, rizom_process
    if link is not None:
        try:
            link.Quit(params)
        except Exception:
            pass
        link = None
    if rizom_process:
        try:
            rizom_process.terminate()
        except Exception:
            pass
        rizom_process = None
    try:
        os.remove(PORT_FILE)
    except Exception:
        pass
    return {"ok": True}


def cmd_get(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        result = link.Get(params)
        return {"ok": True, "result": result}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_get_as_string(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        result = link.GetAsString(params)
        return {"ok": True, "result": result}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_set(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Set(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_select(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Select(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_cut(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Cut(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_weld(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Weld(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_optimize(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Optimize(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_island_groups(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        result = link.IslandGroups(params)
        return {"ok": True, "result": result}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_island_properties(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        result = link.IslandProperties(params)
        return {"ok": True, "result": result}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_uvset(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Uvset(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_deform(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Deform(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_tag(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Tag(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_hotspot(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.Hotspot(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_raster_export(params):
    err = _ensure_connected()
    if err:
        return err
    try:
        link.RasterExport(params)
        return {"ok": True}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


def cmd_execute(params):
    """Generic execute - pass through to any RizomUV API command."""
    err = _ensure_connected()
    if err:
        return err
    try:
        cmd_name = params.pop("command", params.pop("Command", ""))
        if not cmd_name:
            return {"ok": False, "error": "Missing 'command' parameter"}
        result = link.Execute(cmd_name, params)
        return {"ok": True, "result": result}
    except (CZEx, RuntimeError) as e:
        return {"ok": False, "error": str(e)}


# ---- Dispatch ----

COMMANDS = {
    "run": cmd_run,
    "load": cmd_load,
    "unfold": cmd_unfold,
    "pack": cmd_pack,
    "save": cmd_save,
    "quit": cmd_quit,
    "get": cmd_get,
    "get_as_string": cmd_get_as_string,
    "set": cmd_set,
    "select": cmd_select,
    "cut": cmd_cut,
    "weld": cmd_weld,
    "optimize": cmd_optimize,
    "island_groups": cmd_island_groups,
    "island_properties": cmd_island_properties,
    "uvset": cmd_uvset,
    "deform": cmd_deform,
    "tag": cmd_tag,
    "hotspot": cmd_hotspot,
    "raster_export": cmd_raster_export,
    "execute": cmd_execute,
}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: rizomuv_bridge.py <json_command>"}))
        sys.exit(1)

    try:
        cmd = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    op = cmd.get("op", cmd.get("command", "")).lower()
    params = cmd.get("params", {})
    if not params:
        # Allow flat params: {"op": "load", "File.Path": "..."}
        flat = {k: v for k, v in cmd.items() if k not in ("op", "command", "params")}
        if flat:
            params = flat

    handler = COMMANDS.get(op)
    if not handler:
        print(json.dumps({"ok": False, "error": f"Unknown op: {op}", "available": list(COMMANDS.keys())}))
        sys.exit(1)

    result = handler(params)
    print(json.dumps(result, ensure_ascii=False, default=str))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
