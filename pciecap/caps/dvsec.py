from .base import ExtendedCapability

class DVSEC(ExtendedCapability):
    def __init__(self, cfg, offset, version, next_ptr):
        super().__init__(cfg, offset, 0x0023, version, next_ptr)

        # --- Raw fields ---
        self.vendor = cfg.read16(offset + 4)

        # Header1 word (offset +4)
        hdr1 = cfg.read16(offset + 6)
        self.rev = hdr1 & 0xF
        self.length = hdr1 >> 4  # length in bytes

        # Header2
        self.dvsec_id = cfg.read16(offset + 8)

    # -----------------------------
    # Pretty dump (like debugger)
    # -----------------------------
    def dump_raw(self, length=None):
        if length is None:
            length = self.length  # DVSEC length

        start = self.offset
        end = start + length

        print(f"DVSEC @0x{self.offset:03x} RAW:")

        for addr in range(start, end, 16):
            chunk = self.cfg.data[addr:min(addr + 16, end)]
            # hex bytes (memory order)
            hex_bytes = " ".join(f"{b:02x}" for b in chunk)

            print(f"{addr:08x}  {hex_bytes}")

    # -----------------------------
    # Decode fields (spec-aligned)
    # -----------------------------
    def dump_decoded(self):
        hdr = self.cfg.read32(self.offset)

        cap_id = hdr & 0xFFFF
        version = (hdr >> 16) & 0xF
        next_ptr = (hdr >> 20) & 0xFFF

        print(f"DVSEC @0x{self.offset:03x} DECODED:")
        print(f"  ExtCap:")
        print(f"    cap_id   : 0x{cap_id:04x}")
        print(f"    version  : {version}")
        print(f"    next_ptr : 0x{next_ptr:03x}")

        print(f"  DVSEC Header1:")
        print(f"    vendor   : 0x{self.vendor:04x}")
        print(f"    rev      : {self.rev}")
        print(f"    length   : {self.length}")

        print(f"  DVSEC Header2:")
        print(f"    dvsec_id : 0x{self.dvsec_id:04x}")

    # -----------------------------
    # String (short summary)
    # -----------------------------
    def __str__(self):
        return (f"DVSEC @0x{self.offset:x} "
                f"vendor=0x{self.vendor:04x} "
                f"id=0x{self.dvsec_id:04x} "
                f"rev={self.rev} "
                f"len={self.length}")
