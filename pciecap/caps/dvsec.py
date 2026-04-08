from .base import ExtendedCapability

class DVSEC(ExtendedCapability):
    type_name = "dvsec"

    def __init__(self, cfg, offset, version, next_ptr):
        # Does it make sense to hardcode cap_id?
        # It is read and set in the walker routine calling this constructor
        super().__init__(cfg, offset, 0x0023, version, next_ptr)

        # --- Raw fields ---
        self.vendor = cfg.read16(offset + 4)

        # Header1 word (offset +4)
        hdr1 = cfg.read16(offset + 6)
        self.rev = hdr1 & 0xF
        self.length = hdr1 >> 4  # length in bytes

        # Header2
        self.dvsec_id = cfg.read16(offset + 8)

        # Vendor-specific registers (everything after Header2)
        self.vsec_start = offset + 0x0A  # spec-correct ?
        self.vsec_end = offset + self.length
        # protect against malformed length
        self.vsec_end = min(self.vsec_end, len(cfg.data))
        self.vendor_data = cfg.data[self.vsec_start:self.vsec_end]

    # -----------------------------
    # Pretty dump (like debugger)
    # -----------------------------
    def dump_raw(self, length=None):
        if length is None:
            length = self.length  # DVSEC length

        start = self.offset
        end = start + length

        print(f"DVSEC @0x{self.offset:03x} RAW (presented as 32-bit value 0x40302010 and byte sequence (10 20 30 40)):")
        for addr in range(start, end, 4):
            chunk = self.cfg.data[addr:min(addr + 4, end)]

            # Convert bytes to int (little-endian)
            val = int.from_bytes(chunk, "little")

            # Format bytes
            hex_bytes = " ".join(f"{b:02x}" for b in chunk)

            print(f"{addr:08x}: 0x{val:08x} ({hex_bytes})")

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
        print(f"  Vendor-Specific Registers:")
        if not self.vendor_data:
            print("    <none>")
        else:
            for i in range(0, len(self.vendor_data), 4):
                chunk = self.vendor_data[i:i+4]

                # pad if needed
                if len(chunk) < 4:
                    chunk = chunk + bytes(4 - len(chunk))

                val = int.from_bytes(chunk, "little")
                hex_bytes = " ".join(f"{b:02x}" for b in chunk)

                print(f"    [{i:02x}]  0x{val:08x} ({hex_bytes})")


    # -----------------------------
    # String (short summary)
    # -----------------------------
    def __str__(self):
        return (f"DVSEC @0x{self.offset:x} "
                f"vendor=0x{self.vendor:04x} "
                f"id=0x{self.dvsec_id:04x} "
                f"rev={self.rev} "
                f"len={self.length}")

    def to_dict(self):
        return {
            "type": self.type_name,
            "offset": f"0x{self.offset:03x}",

            "ExtCap": {
                "cap_id": f"0x{self.cap_id:04x}",
                "version": self.version,
                "next_ptr": f"0x{self.next_ptr:03x}",
            },

            "DVSEC Header1": {
                "vendor": f"0x{self.vendor:04x}",
                "rev": self.rev,
                "length": self.length,
            },

            "DVSEC Header2": {
                "dvsec_id": f"0x{self.dvsec_id:04x}",
            },

            "Vendor-Specific Registers": {
                "raw": " ".join(f"{b:02x}" for b in self.vendor_data)
            },
        }
