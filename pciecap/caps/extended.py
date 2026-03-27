from .dvsec import DVSEC
from .ide import IDECapability

EXT_CAP_CLASSES = {
    0x0023: DVSEC,
    0x0030: IDECapability,
}

def walk_extended_caps(cfg):
    caps = []

    off = 0x100
    visited = set()

    while off and off not in visited:
        visited.add(off)

        hdr = cfg.read32(off)
        cap_id = hdr & 0xFFFF
        version = (hdr >> 16) & 0xF
        next_ptr = (hdr >> 20) & 0xFFF

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
        off = next_ptr

    return caps
