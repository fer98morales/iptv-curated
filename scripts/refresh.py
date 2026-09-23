#!/usr/bin/env python3
"""
Refresh curated IPTV-org playlists while preserving the local whitelist.

Sources:
  https://iptv-org.github.io/iptv/countries/mx.m3u
  https://iptv-org.github.io/iptv/countries/us.m3u

The config files contain tvg-id values selected for each playlist.
If IPTV-org changes the stream URL/logo/name for a selected channel,
this script picks up the new entry automatically.
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLAYLISTS = {
    "mexico": {
        "source": "https://iptv-org.github.io/iptv/countries/mx.m3u",
        "config": ROOT / "config" / "mexico.json",
        "output": ROOT / "playlists" / "mexico.m3u",
    },
    "usa": {
        "source": "https://iptv-org.github.io/iptv/countries/us.m3u",
        "config": ROOT / "config" / "usa.json",
        "output": ROOT / "playlists" / "usa.m3u",
    },
}

def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "iptv-curated-refresh/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")

def parse_m3u(text: str):
    lines = [line.strip() for line in text.splitlines()]
    entries = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i]
            j = i + 1
            # Preserve any IPTV-org directives between EXTINF and the URL.
            middle = []
            while j < len(lines) and (not lines[j] or lines[j].startswith("#")):
                if lines[j]:
                    middle.append(lines[j])
                j += 1
            if j < len(lines):
                url = lines[j]
                tvg = re.search(r'tvg-id="([^"]*)"', extinf)
                if tvg:
                    entries.append({
                        "tvg_id": tvg.group(1),
                        "extinf": extinf,
                        "middle": middle,
                        "url": url,
                    })
            i = j
        i += 1
    return entries

def replace_group(extinf: str, group: str) -> str:
    if 'group-title="' in extinf:
        return re.sub(r'group-title="[^"]*"', f'group-title="{group}"', extinf)
    # Insert before the comma separating attributes from channel name.
    comma = extinf.find(",")
    if comma == -1:
        return extinf + f' group-title="{group}"'
    return extinf[:comma] + f' group-title="{group}"' + extinf[comma:]

def refresh_one(name: str, spec: dict) -> None:
    wanted = json.loads(spec["config"].read_text(encoding="utf-8"))
    source_entries = parse_m3u(fetch(spec["source"]))
    by_id = {entry["tvg_id"]: entry for entry in source_entries}

    output = ["#EXTM3U"]
    missing = []

    for channel in wanted:
        tvg_id = channel["tvg_id"]
        entry = by_id.get(tvg_id)
        if not entry:
            missing.append(f'{tvg_id} ({channel.get("name","")})')
            continue

        extinf = replace_group(entry["extinf"], channel["group"])
        output.append(extinf)
        output.extend(entry["middle"])
        output.append(entry["url"])

    spec["output"].parent.mkdir(parents=True, exist_ok=True)
    spec["output"].write_text("\r\n".join(output) + "\r\n", encoding="utf-8", newline="")

    print(f"{name}: wrote {len(output)} lines; selected {len(wanted) - len(missing)}/{len(wanted)} channels")
    if missing:
        print(f"{name}: WARNING, {len(missing)} selected channels were not found upstream:")
        for item in missing:
            print("  -", item)

def main():
    for name, spec in PLAYLISTS.items():
        refresh_one(name, spec)

if __name__ == "__main__":
    main()
