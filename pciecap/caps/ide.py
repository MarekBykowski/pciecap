from .base import ExtendedCapability

class IDECapability(ExtendedCapability):
    def __init__(self, cfg, offset, version, next_ptr):
        super().__init__(cfg, offset, 0x0030, version, next_ptr)

        self.cap = cfg.read32(offset + 4)
        self.ctrl = cfg.read32(offset + 8)

    @property
    def supported(self):
        return bool(self.cap & 0x1)

    @property
    def enabled(self):
        return bool(self.ctrl & 0x1)

    def __str__(self):
        return (f"IDE @0x{self.offset:x} "
                f"supported={self.supported} "
                f"enabled={self.enabled}")
