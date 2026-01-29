# Python TextFSM CMDB Parser

This repository provides a **simple, scalable, and beginner-friendly** way to parse raw CLI command outputs into structured CSV files using **TextFSM**.

The design intentionally avoids complex regex indexing (like NTC CliTable) and instead uses:
- clear folder structure
- human-readable `mapping.json`
- predictable filename conventions

It supports **multi-vendor, multi-platform** environments.

---

## Folder Structure

```
.
├── templates/
├── files/
│   ├── cisco_ios/
│   ├── cisco_nxos/
│   ├── linux/
│   └── zyxel_os/
├── mapping.json
├── config.json
├── parse_to_csv.py
└── README.md
```

---

## Filename Convention (IMPORTANT)

All raw command output files **must** follow:

```
{{command_with_underscores}}_{{hostname}}.txt
```

Examples:
```
show_cdp_neighbors_sw1.txt
show_cdp_neighbors_ciscol224_L2_1.txt
ip_address_show_node01.txt
dmidecode_-t_memory_serverA.txt
```

Hostname may contain underscores.

---

## mapping.json

Maps **platform → command → TextFSM template**.

Example:
```json
{
  "cisco_ios": {
    "show cdp neighbors": "cisco_ios_show_cdp_neighbors.textfsm"
  },
  "linux": {
    "ip address show": "linux_ip_address_show.textfsm"
  }
}
```

Matching rules:
1. `_` in filename → space
2. Longest prefix wins
3. Arguments supported

---

## config.json (optional)

Used for platform aliasing.

```json
{
  "platform_aliases": {
    "netscaler_adc": "citrix_adc",
    "ios": "cisco_ios"
  }
}
```

---

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python parse_to_csv.py
```

CSV output is written to:
```
files/
```

---

## Validate JSON

```powershell
python -m json.tool mapping.json
```

---

This project is designed as a **pure parsing layer** for CMDB, inventory, and audit use cases.
