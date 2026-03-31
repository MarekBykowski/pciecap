### PCIeCap

Welcome to the pciecap wiki!

`pciecap` is a Python tool for parsing and decoding PCIe Extended Capabilities from the PCI configuration space exposed by the Linux kernel:

`/sys/bus/pci/devices/{bdf}/config`

⚠️ Requirements

Access to the PCI configuration space requires root privileges.

This means the tool can only be used on systems where you have sufficient permissions, such as:
* GNR
* Wilson City
* QEMU
* Simics

It will not work on restricted environments (e.g., Intel servers like ION) where root access is unavailable.

### Features
Walks through all legacy and extended PCIe capabilities. Decodes:
* DVSEC (Designated Vendor-Specific Extended Capability)
* IDE (Integrity and Data Encryption) capability structures

Export formats:
* JSON (default)
* YAML

### Installation
```
git clone https://github.com/MarekBykowski/pciecap.git
cd pciecap
make install-local
``` 

### Show help
```
sudo pciecap -h
```
```
usage: pciecap [-h] [--yaml] target

PCIe capability inspection tool

positional arguments:
  target      BDF (e.g. 0000:00:1c.0) or 'rootports'

optional arguments:
  -h, --help  show this help message and exit
  --yaml      Output YAML instead of default JSON
```

### Listing Root Ports

You can list all root ports available on your system. This is useful when identifying devices that may contain IDE capabilities.

Example output:
```
0000:14:06.0
0000:14:07.0
0000:14:08.0
0000:14:09.0
0000:29:02.0
0000:b7:02.0
```

### Inspecting a Device

Run the tool with a specific BDF:
```
sudo pciecap <BDF>
```

Example:
```
sudo pciecap 0000:29:02.0
```

Output:
```
Device 0000:29:02.0
  Vendor: 0x8086
  Device: 0x0db0

[Legacy Capabilities]
  - Cap @0x40 ID=0x10
  - Cap @0xa0 ID=0x01
  - Cap @0x94 ID=0x0d
  - Cap @0x80 ID=0x05
[Extended Capabilities]
[off=0x100 id=0x0001 ver=0x2 next=0x220]
[off=0x220 id=0x000d ver=0x1 next=0x190]

IDE capability raw dump example:

IDE @0x304 RAW:
00000304  30 00 01 b2
00000308  a3 00 03 00
```

### Logging Output

To capture both stdout and stderr into a file:
```
sudo pciecap <BDF> 2>&1 | tee out.log
vim out.log
```

#### Notes
The tool currently focuses on DVSEC and IDE decoding.
Other capabilities are enumerated but not yet fully decoded.
