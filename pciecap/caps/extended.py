try:
    import yaml
except ImportError:
    yaml = None

import json
from collections import defaultdict
from .dvsec import DVSEC
from .ide import IDECapability

EXT_CAP_CLASSES = {
    0x0023: DVSEC,
    0x0030: IDECapability,
}

def fmt_cap(cap):
    return (
        f"[off=0x{cap['offset']:03x} "
        f"id=0x{cap['id']:04x} "
        f"ver=0x{cap['version']:x} "
        f"next=0x{cap['next']:03x}]"
    )

def walk_extended_caps(cfg, bdf, yaml_enable=False, json_enable=False):

    if yaml_enable and yaml is None:
        print("Warning: YAML requested but PyYAML not installed � skipping")
        yaml_enable = False

    caps = []

    off = 0x100
    visited = set()
    size = len(cfg.data)

    while off and off not in visited:
        # bound check
        if off < 0x100 or off + 4 > size:
            break

        visited.add(off)

        hdr = cfg.read32(off)

        # no capability present
        if hdr == 0:
            break

        cap_id = hdr & 0xFFFF
        version = (hdr >> 16) & 0xF
        next_ptr = (hdr >> 20) & 0xFFF

        # sanity check next pointer
        if next_ptr != 0 and (next_ptr < 0x100 or next_ptr >= size):
            break

        cls = EXT_CAP_CLASSES.get(cap_id)

        if cls:
            cap = cls(cfg, off, version, next_ptr)
        else:
            cap = {
                "offset": off,
                "id": cap_id,
                "version": version,
                "next": next_ptr,
            }

        caps.append(cap)

        if next_ptr == off:
            break

        off = next_ptr

    if yaml_enable or json_enable:
        grouped = defaultdict(list)

        for cap in caps:
            if hasattr(cap, "to_dict"):
                cap_dict = cap.to_dict()
                key = cap_dict.get("type", "unknown")
            else:
                cap_dict = cap
                key = "unknown"

            grouped[key].append(cap_dict)

        for key, items in grouped.items():
            data = {
                "bdf": bdf,   # <-- make sure bdf is passed to this function
                "type": key,
                "caps": items
            }

            if yaml_enable:
                with open(f"{key}.yaml", "w") as f:
                    yaml.dump(data, f, sort_keys=False)

            if json_enable:
                with open(f"{key}.json", "w") as f:
                   json.dump(data, f, indent=2)

    return caps
