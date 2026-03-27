def walk_legacy_caps(cfg):
    caps = []

    cap_ptr = cfg.read8(0x34)
    visited = set()

    while cap_ptr and cap_ptr not in visited:
        visited.add(cap_ptr)

        cap_id = cfg.read8(cap_ptr)
        next_ptr = cfg.read8(cap_ptr + 1)

        caps.append({
            "offset": cap_ptr,
            "id": cap_id,
        })

        cap_ptr = next_ptr

    return caps
