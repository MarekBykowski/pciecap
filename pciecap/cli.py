import sys
import subprocess
import argparse

from .config import PCIConfig
from .caps.legacy import walk_legacy_caps
from .caps.extended import walk_extended_caps, fmt_cap
from .caps.dvsec import DVSEC

def get_root_ports():
    out = subprocess.check_output(["lspci", "-D", "-vvv"], text=True)

    root_ports = []
    bdf = None

    for line in out.splitlines():
        if line and line[0].isalnum():
            bdf = line.split()[0]

        if "Root Port" in line and bdf:
            root_ports.append(bdf)

    return root_ports

def main():
    parser = argparse.ArgumentParser(
        prog="pciecap",
        description="PCIe capability inspection tool"
    )

    parser.add_argument("target", help="BDF (e.g. 0000:00:1c.0) or 'rootports'")
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Output YAML instead of default JSON"
    )

    args = parser.parse_args()

    # --- format selection (JSON default) ---
    use_yaml = args.yaml
    use_json = not args.yaml

    # --- YAML dependency check ---
    if use_yaml:
        try:
            import yaml  # noqa: F401
        except ImportError:
            print("ERROR: YAML requires PyYAML (pip install pciecap[yaml])")
            sys.exit(1)

    # --- Root ports mode ---
    if args.target == "rootports":
        for bdf in get_root_ports():
            print(bdf)
        return

    bdf = args.target

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
    for cap in walk_extended_caps(cfg, bdf, yaml_enable=use_yaml, json_enable=use_json):
        if hasattr(cap, "dump_raw") and hasattr(cap, "dump_decoded"):
            cap.dump_raw()
            cap.dump_decoded()
        else:
            #print(f"[{cap}]")
            print(fmt_cap(cap))

if __name__ == "__main__":
    main()
