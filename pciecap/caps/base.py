class Capability:
    def __init__(self, cfg, offset, cap_id):
        self.cfg = cfg
        self.offset = offset
        self.cap_id = cap_id

    def __str__(self):
        return f"Cap(id=0x{self.cap_id:x} @0x{self.offset:x})"


class ExtendedCapability(Capability):
    def __init__(self, cfg, offset, cap_id, version, next_ptr):
        super().__init__(cfg, offset, cap_id)
        self.version = version
        self.next_ptr = next_ptr
