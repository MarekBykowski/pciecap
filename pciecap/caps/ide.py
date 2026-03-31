import yaml
from .base import ExtendedCapability

def _yn(v):
    return "Yes" if v else "No"

class IDECapability(ExtendedCapability):
    type_name = "ide"

    def __init__(self, cfg, offset, version, next_ptr):
        super().__init__(cfg, offset, 0x0030, version, next_ptr)

        self.debug = False

        self.cap_start = offset
        self.cap_end = None

        # Header, capability, control
        self.hdr = cfg.read32(offset)
        self.cap = cfg.read32(offset + 4)
        self.ctrl = cfg.read32(offset + 8)

        # --- Header ---
        self.cap_id  = self.hdr & 0xFFFF
        self.version = (self.hdr >> 16) & 0xF
        self.next_ptr = (self.hdr >> 20) & 0xFFF

        # --- Capability ---
        self.link_ide_supported       = bool(self.cap & (1 << 0))
        self.selective_ide_supported  = bool(self.cap & (1 << 1))
        self.flow_through_supported   = bool(self.cap & (1 << 2))
        self.partial_hdr_enc          = bool(self.cap & (1 << 3))
        self.aggregation_supported    = bool(self.cap & (1 << 4))
        self.pcrc_supported           = bool(self.cap & (1 << 5))
        self.ide_km_supported         = bool(self.cap & (1 << 6))
        self.sel_ide_cfg_supported    = bool(self.cap & (1 << 7))
        # Decode algorithms
        self.algorithms  = (self.cap >> 8) & 0x1F #bits 8-12
        self.algorithms_decoded = []
        if self.algorithms == 0:
            self.algorithms_decoded.append("AES-GCM-256 (96b MAC)")
        if not self.algorithms_decoded:
            self.algorithms_decoded.append("None / Reserved")
        # Number of TCs Supported for Link IDE
        #   000b -> 1 TC supported
        #   001b -> 2 TCs, etc.
        #   So many TCs so many Link IDE blocks
        self.num_tcs = ((self.cap >> 13) & 0x7) + 1       # bits 13-15
        # Number of Selective IDE Streams Supported
        #   0 -> 1 Stream
        #   1 -> 2 Streams, etc
        self.num_sel_ide_streams = ((self.cap >> 16) & 0xFF) + 1  # bits 16-23

        self.num_link_blocks = self.num_tcs
        self.num_sel_blocks  = self.num_sel_ide_streams

        # --- Control ---
        self.flow_through_ide_stream_enabled  = bool(self.ctrl & (1 << 2))

        self.link_blocks = []
        self.sel_blocks = []

        self._parse_blocks()

    # -----------------------------
    # RAW dump
    # -----------------------------
    def dump_raw(self):
        start = self.cap_start
        end = self.cap_end

        print(f"IDE @0x{self.offset:03x} RAW:")

        for addr in range(start, end, 4):
            chunk = self.cfg.data[addr:min(addr + 4, end)]
            # pad if last chunk < 4 bytes (edge safety)
            #chunk = chunk + bytes(4 - len(chunk))
            hex_bytes = " ".join(f"{b:02x}" for b in chunk)
            print(f"{addr:08x}  {hex_bytes}")

    # -----------------------------
    # Parse blocks
    # -----------------------------
    def _parse_blocks(self):
        off = self.offset + 0x0C

        # --- Link IDE blocks ---
        for _ in range(self.num_link_blocks):
            ctrl = self.cfg.read32(off)
            status = self.cfg.read32(off + 4)

            self.link_blocks.append({
                "control": ctrl,
                "status": status,
                "offset": off,
            })

            off += 8

        # --- Selective IDE blocks ---
        for _ in range(self.num_sel_blocks):
            block = {
                "cap": self.cfg.read32(off + 0x00),
                "ctrl": self.cfg.read32(off + 0x04),
                "status": self.cfg.read32(off + 0x08),
                "rid1": self.cfg.read32(off + 0x0C),
                "rid2": self.cfg.read32(off + 0x10),
                "offset": off,
                "addr_blocks": []
            }

            # Read Selective IDE Stream Capability Register (offset 0x00)
            cap = self.cfg.read32(off + 0x00)

            # Bits [3:0] -> Number of Address Association Register Blocks
            num_addr_blocks = cap & 0xF

            off += 0x14  # move past fixed part (up to rid2)

            for i in range(num_addr_blocks):
                addr_block = {
                    "addr1": self.cfg.read32(off + 0x00),  # fill correct offsets
                    "addr2": self.cfg.read32(off + 0x04),
                    "addr3": self.cfg.read32(off + 0x08),
                    "offset": off,
                }

                block["addr_blocks"].append(addr_block)
                self.cap_end = off
                off += 0x0C  # 3 DW per block

            self.sel_blocks.append(block)

            #off += 32

    # -----------------------------
    # DECODED dump
    # -----------------------------
    def dump_decoded(self):
        print(f"IDE @0x{self.offset:03x} DECODED:")

        # --- Header ---
        cap_id  = self.hdr & 0xFFFF
        version = (self.hdr >> 16) & 0xF
        next_ptr = (self.hdr >> 20) & 0xFFF

        print("  Header:")
        print(f"    raw     : 0x{self.hdr:08x}")
        print(f"    id      : 0x{cap_id:04x}")
        print(f"    version : {version}")
        print(f"    next    : 0x{next_ptr:03x}")

        print("  Capability:")
        print(f"    raw : 0x{self.cap:08x}")

        print("    Features:")
        print(f"      Link IDE Stream           : {_yn(self.link_ide_supported)}")
        print(f"      Selective IDE Streams     : {_yn(self.selective_ide_supported)}")
        print(f"      Flow-Through IDE          : {_yn(self.flow_through_supported)}")
        print(f"      Partial Header Encryption : {_yn(self.partial_hdr_enc)}")
        print(f"      Aggregation               : {_yn(self.aggregation_supported)}")
        print(f"      PCRC                      : {_yn(self.pcrc_supported)}")
        print(f"      IDE_KM Protocol           : {_yn(self.ide_km_supported)}")
        print(f"      Selective IDE CFG Req     : {_yn(self.sel_ide_cfg_supported)}")

        print("    Parameters:")
        print(f"      Num TCs                   : {self.num_tcs}")
        print(f"      Algorithms (bitmask)      : 0x{self.algorithms:x}")
        print(f"      Algorithms                : {', '.join(self.algorithms_decoded)}")
        print(f"      Num Selective IDE Streams : {self.num_sel_ide_streams}")

        # --- Control ---
        print("  Control:")
        print(f"    raw : 0x{self.ctrl:08x}")

        print("    Features:")
        print(f"      Flow through IDE stream   : {_yn(self.flow_through_ide_stream_enabled)}")

        # --- Link blocks ---
        print("  Link IDE Blocks:")
        for i, b in enumerate(self.link_blocks):
            print(f"    [{i}] ctrl=0x{b['control']:08x} status=0x{b['status']:08x}")
            if self.debug:
                print(f"          offset=0x{b['offset']:03x}")

        # --- Selective blocks ---
        print("  Selective IDE Blocks:")
        for i, b in enumerate(self.sel_blocks):
            print(f"    [{i}]")
            print(f"      cap   = 0x{b['cap']:08x}")
            print(f"      ctrl  = 0x{b['ctrl']:08x}")
            print(f"      status= 0x{b['status']:08x}")
            print(f"      rid1  = 0x{b['rid1']:08x}")
            print(f"      rid2  = 0x{b['rid2']:08x}")
            if self.debug:
                print(f"      offset = 0x{b['offset']:03x}")

            for j, ab in enumerate(b["addr_blocks"]):
                print(f"      Address Association Block [{j}]")
                print(f"        addr1 = 0x{ab['addr1']:08x}")
                print(f"        addr2 = 0x{ab['addr2']:08x}")
                print(f"        addr3 = 0x{ab['addr3']:08x}")
                if self.debug:
                    print(f"        offset = 0x{ab['offset']:03x}")

    def __str__(self):
        return f"IDE @0x{self.offset:x}"

    def to_dict(self):
        # --- Link blocks ---
        link_blocks_list = []

        for b in self.link_blocks:
            block = {}
            block["control"] = f"0x{b['control']:08x}"
            block["status"]  = f"0x{b['status']:08x}"
            link_blocks_list.append(block)

        # --- Selective blocks ---
        selective_blocks_list = []

        for b in self.sel_blocks:
            block = {}
            block["cap"]    = f"0x{b['cap']:08x}"
            block["ctrl"]   = f"0x{b['ctrl']:08x}"
            block["status"] = f"0x{b['status']:08x}"
            block["rid1"]   = f"0x{b['rid1']:08x}"
            block["rid2"]   = f"0x{b['rid2']:08x}"

            # --- Address blocks ---
            addr_blocks_list = []

            for ab in b["addr_blocks"]:
                addr_block = {}
                addr_block["addr1"] = f"0x{ab['addr1']:08x}"
                addr_block["addr2"] = f"0x{ab['addr2']:08x}"
                addr_block["addr3"] = f"0x{ab['addr3']:08x}"
                addr_blocks_list.append(addr_block)

            block["addr_blocks"] = addr_blocks_list
            selective_blocks_list.append(block)

        return {
            "type": self.type_name,

            "offset": f"0x{self.offset:03x}",

            # --- Header ---
            "header": {
                "raw": f"0x{self.hdr:08x}",
                "cap_id": f"0x{self.cap_id:04x}",
                "version": self.version,
                "next_ptr": f"0x{self.next_ptr:03x}",
            },

            # --- Capability ---
            "capability": {
                "raw": f"0x{self.cap:08x}",

                "features": {
                    "link_ide": self.link_ide_supported,
                    "selective_ide": self.selective_ide_supported,
                    "flow_through": self.flow_through_supported,
                    "partial_header_encryption": self.partial_hdr_enc,
                    "aggregation": self.aggregation_supported,
                    "pcrc": self.pcrc_supported,
                    "ide_km": self.ide_km_supported,
                    "sel_ide_cfg_req": self.sel_ide_cfg_supported,
                },

                "parameters": {
                    "num_tcs": self.num_tcs,
                    "algorithms_raw": f"0x{self.algorithms:08x}",  # ?? fixed width
                    "algorithms": self.algorithms_decoded,
                    "num_sel_ide_streams": self.num_sel_ide_streams,
                },
            },

            # --- Control ---
            "control": {
                "raw": f"0x{self.ctrl:08x}",
                "flow through IDE stream" : self.flow_through_ide_stream_enabled,
            },

            # --- Blocks (pass-through, but assume they already format hex internally) ---
            "link_blocks": link_blocks_list,
            "selective_blocks": selective_blocks_list,
        }
