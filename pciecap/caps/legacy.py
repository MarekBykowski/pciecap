def walk_legacy_caps(cfg):
    caps = []

    cap_ptr = cfg.read8(0x34)
    visited = set()
    size = len(cfg.data)

    while cap_ptr:
        # bounds
        if cap_ptr < 0x40 or cap_ptr >= 0x100:
            break

        if cap_ptr in visited:
            break

        visited.add(cap_ptr)

        # safe read
        if cap_ptr >= size:
            break

        cap_id = cfg.read8(cap_ptr)

        # ensure next pointer exists
        if cap_ptr + 1 >= size:
            break

        next_ptr = cfg.read8(cap_ptr + 1)

        caps.append({
            "offset": cap_ptr,
            "id": cap_id,
            "next": next_ptr
        })

        # termination conditions
        if next_ptr == 0 or next_ptr == cap_ptr:
            break

        cap_ptr = next_ptr

    return caps
