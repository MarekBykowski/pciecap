from .base import ExtendedCapability

class DVSEC(ExtendedCapability):
    def __init__(self, cfg, offset, version, next_ptr):
        super().__init__(cfg, offset, 0x0023, version, next_ptr)

        self.vendor = cfg.read16(offset + 4)
        self.rev = cfg.read8(offset + 6)
        self.length = cfg.read16(offset + 6) >> 4
        self.dvsec_id = cfg.read16(offset + 8)

    def __str__(self):
        return (f"DVSEC @0x{self.offset:x} "
                f"vendor=0x{self.vendor:04x} "
                f"id=0x{self.dvsec_id:04x} "
                f"rev={self.rev}")
