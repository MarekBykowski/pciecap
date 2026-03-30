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
