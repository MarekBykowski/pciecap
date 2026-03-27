import sys
from .config import PCIConfig
from .caps.legacy import walk_legacy_caps
from .caps.extended import walk_extended_caps


def main():
    if len(sys.argv) != 2:
        print("Usage: pciecap <BDF>")
        sys.exit(1)

    bdf = sys.argv[1]

    cfg = PCIConfig(bdf)

    vendor = cfg.read16(0x00)
    device = cfg.read16(0x02)

    print(f"Device {bdf}")
    print(f"  Vendor: 0x{vendor:04x}")
    print(f"  Device: 0x{device:04x}")

    print("\n[Legacy Capabilities]")
    for cap in walk_legacy_caps(cfg):
        print(f"  - Cap @0x{cap['offset']:02x} ID=0x{cap['id']:02x}")

    print("\n[Extended Capabilities]")
    for cap in walk_extended_caps(cfg):
        print(f"  - {cap}")


if __name__ == "__main__":
    main()
