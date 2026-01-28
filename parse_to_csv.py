#!/usr/bin/env python3
import argparse
import csv
import io
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

import textfsm

HOST_CMD_RE = re.compile(r"^(?P<host>.+?)_(?P<cmd>.+)$", re.IGNORECASE)

def split_host_and_command(stem: str) -> Tuple[str, str]:
    m = HOST_CMD_RE.match(stem)
    if not m:
        return "", stem
    return m.group("host"), m.group("cmd")

def normalize_template(text: str) -> str:
    # Protect against indentation issues that cause "Invalid state name" on some Windows setups.
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    in_state = False
    for line in lines:
        if line.startswith("Value ") or line.strip() == "" or line.lstrip().startswith("#"):
            out.append(line)
            continue
        if not line.startswith((" ", "\t")) and not line.startswith("^"):
            in_state = True
            out.append(line)
            continue
        if line.startswith("^") and in_state:
            out.append("  " + line)
            continue
        out.append(line)
    return "\n".join(out).rstrip() + "\n"

def parse_text(template_path: Path, raw: str) -> List[Dict[str, Any]]:
    tpl_text = normalize_template(template_path.read_text(encoding="utf-8", errors="replace"))
    fsm = textfsm.TextFSM(io.StringIO(tpl_text))
    parsed = fsm.ParseText(raw)
    headers = fsm.header
    return [{headers[i].lower(): row[i] for i in range(len(headers))} for row in parsed]

def write_csv(path: Path, rows: List[Dict[str, Any]]):
    cols = []
    for r in rows:
        for k in r.keys():
            if k != "hostname" and k not in cols:
                cols.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["hostname"] + cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def resolve_template(platform_map: Dict[str, str], cli_cmd: str) -> Optional[str]:
    """
    Supports:
    - exact match: 'show cdp neighbors'
    - prefix match: 'ping' matches 'ping 8.8.8.8'
    Longest prefix wins.
    """
    cli_cmd = cli_cmd.strip().lower()
    if cli_cmd in platform_map:
        return platform_map[cli_cmd]

    best_key = None
    for key in platform_map.keys():
        k = key.strip().lower()
        if cli_cmd.startswith(k + " ") or cli_cmd == k:
            if best_key is None or len(k) > len(best_key):
                best_key = k
    if best_key is not None:
        return platform_map[best_key]
    return None

def main():
    ap = argparse.ArgumentParser(description="Auto-parse samples_txt/<platform>/*.txt using mapping.json")
    ap.add_argument("--root", default="samples_txt", help="Root folder containing per-platform subfolders")
    ap.add_argument("--templates-dir", default="templates")
    ap.add_argument("--mapping", default="mapping.json")
    ap.add_argument("--config", default="config.json", help="Optional config with platform_aliases")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--platform", default="", help="Optional: parse only this platform folder (e.g. cisco_ios)")
    args = ap.parse_args()

    root = Path(args.root)
    templates_dir = Path(args.templates_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    config = {}
    cfg_path = Path(args.config)
    if cfg_path.exists():
        config = json.loads(cfg_path.read_text(encoding="utf-8"))
    aliases = config.get("platform_aliases", {})

    platform_dirs = [p for p in root.iterdir() if p.is_dir()]
    if args.platform:
        platform_dirs = [root / args.platform]

    for platform_dir in sorted(platform_dirs):
        folder_platform = platform_dir.name
        resolved_platform = aliases.get(folder_platform, folder_platform)

        platform_map = mapping.get(resolved_platform, {})
        if not platform_map:
            print(f"SKIP: No mapping for platform '{resolved_platform}' (folder '{folder_platform}')")
            continue

        per_cmd = defaultdict(list)

        for txt_file in sorted(platform_dir.glob("*.txt")):
            host, cmd_key = split_host_and_command(txt_file.stem)
            cli_cmd = cmd_key.replace("_", " ").lower()

            tpl_name = resolve_template(platform_map, cli_cmd)
            if not tpl_name:
                continue

            tpl_path = templates_dir / tpl_name
            if not tpl_path.exists():
                print(f"ERROR: template not found: {tpl_path}")
                continue

            raw = txt_file.read_text(encoding="utf-8", errors="replace")
            try:
                records = parse_text(tpl_path, raw)
            except Exception as e:
                print(f"ERROR: parse failed for {txt_file}: {e}")
                continue

            for r in records:
                r["hostname"] = host
                per_cmd[cmd_key].append(r)

        for cmd_key, rows in sorted(per_cmd.items()):
            out_name = f"{resolved_platform}_{cmd_key}.csv"
            write_csv(out_dir / out_name, rows)
            print(f"Wrote {out_name} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
