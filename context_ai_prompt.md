# Context: TextFSM CMDB Parsing System

This document provides **context for humans and AI systems** interacting with this repository.

---

## System Purpose

- Convert raw CLI outputs into structured CSV
- Support multi-vendor platforms
- Be deterministic and beginner-friendly
- Avoid regex-based index systems

---

## Core Concepts

### Platform
- One subfolder under `samples_txt/`
- One key in `mapping.json`

Examples:
- cisco_ios
- linux
- zyxel_os

---

### Filename Semantics

```
{{command_with_underscores}}_{{hostname}}.txt
```

Rules:
- Hostname may contain `_`
- Command is matched via known mapping keys
- Longest matching command prefix is used

---

### Mapping Resolution

1. Detect platform folder
2. Apply alias (if configured)
3. Extract command from filename
4. Match command to mapping.json
5. Load TextFSM template
6. Parse output
7. Write CSV

---

### Output Model

- One CSV per command
- Filename format:
  ```
  {{platform}}_{{command_with_underscores}}.csv
  ```
- Each row includes `hostname`

---

## What This System Does NOT Do

- No device access
- No SSH
- No command execution
- No dynamic discovery
- No regex-based template selection

---

## Design Philosophy

> Explicit is better than clever

If parsing fails:
- Fix filenames
- Fix mapping.json
- Fix template

Do not add complexity unless required.
