import struct

CONFIG_SIZE = 4096

class PCIConfig:
    def __init__(self, bdf):
        self.bdf = bdf
        path = f"/sys/bus/pci/devices/{bdf}/config"
        with open(path, "rb") as f:
            self.data = f.read(CONFIG_SIZE)

    def read8(self, off):
        return self.data[off]

    def read16(self, off):
        return struct.unpack_from("<H", self.data, off)[0]

    def read32(self, off):
        return struct.unpack_from("<I", self.data, off)[0]

    def read8o(self, off):
        val = self.read8(off)
        return {
            "offset": f"0x{off:03x}",
            "value": f"0x{val:02x}"
        }

    def read16o(self, off):
        val = self.read16(off)
        return {
            "offset": f"0x{off:03x}",
            "value": f"0x{val:04x}"
        }

    def read32o(self, off):
        val = self.read32(off)
        return {
            "offset": f"0x{off:03x}",
            "value": f"0x{val:08x}"
        }
    """
    Format a 32-bit integer as little-endian byte sequence.
    Example:
        0xb2010030 -> "30 00 01 b2"
    """
    def fmt32(self, val):
        b = val.to_bytes(4, "little")
        return " ".join(f"{x:02x}" for x in b)
