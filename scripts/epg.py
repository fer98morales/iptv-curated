#!/usr/bin/env python3
"""Prepare IPTV-org's grabber input and publish validated, feed-matched XMLTV."""
import argparse
import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PLAYLISTS = ('mexico', 'usa', 'sports')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def prepare(destination):
    wanted = {c['tvg_id'] for name in PLAYLISTS for c in read_json(ROOT / 'config' / f'{name}.json')}
    channels = ET.Element('channels')
    seen = set()
    for source in read_json(ROOT / 'config/epg.json'):
        channel_id = source['tvg_id']
        if channel_id not in wanted:
            continue
        if channel_id in seen:
            raise ValueError(f'Duplicate EPG mapping: {channel_id}')
        seen.add(channel_id)
        ET.SubElement(channels, 'channel', {
            'site': source['site'], 'site_id': source['site_id'],
            'lang': source['lang'], 'xmltv_id': channel_id,
        }).text = source['name']
    destination.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(channels).write(destination, encoding='utf-8', xml_declaration=True)
    print(f'Prepared {len(seen)} exact feed mappings')


def timestamp(value):
    # Reject ambiguous timestamps: never silently assume a local timezone.
    return datetime.strptime(value, '%Y%m%d%H%M%S %z').astimezone(timezone.utc)


def programmes(path, now):
    result = {}
    if not path.exists():
        return result
    tv = ET.parse(path).getroot()
    if tv.tag != 'tv':
        raise ValueError(f'Not XMLTV: {path}')
    for entry in tv.findall('programme'):
        try:
            start, stop = timestamp(entry.get('start', '')), timestamp(entry.get('stop', ''))
        except ValueError:
            continue
        if not entry.findtext('title', '').strip() or not start < stop:
            continue
        if stop <= now or start > now + timedelta(days=7):
            continue
        result.setdefault(entry.get('channel'), []).append(entry)
    return result


def publish(source):
    now = datetime.now(timezone.utc)
    fresh = programmes(source, now)
    if not fresh:
        raise ValueError('No current/future programmes received; existing guides left untouched')
    outdir = ROOT / 'epg'
    outdir.mkdir(exist_ok=True)
    report = {'generated_at': now.isoformat(), 'playlists': {}}
    outputs = {}
    for name in PLAYLISTS:
        wanted = read_json(ROOT / 'config' / f'{name}.json')
        old = programmes(outdir / f'{name}.xml', now)
        tv = ET.Element('tv', {'generator-info-name': 'iptv-curated / iptv-org/epg'})
        covered, retained, missing, current = [], [], [], []
        count = 0
        for channel in wanted:
            channel_id = channel['tvg_id']
            entries = fresh.get(channel_id) or old.get(channel_id) or []
            if not entries:
                missing.append(channel_id)
                continue
            covered.append(channel_id)
            if channel_id not in fresh:
                retained.append(channel_id)
            node = ET.SubElement(tv, 'channel', {'id': channel_id})
            ET.SubElement(node, 'display-name').text = channel['name']
            seen = set()
            for entry in sorted(entries, key=lambda e: timestamp(e.get('start'))):
                key = (entry.get('start'), entry.get('stop'), entry.findtext('title'))
                if key in seen:
                    continue
                seen.add(key)
                tv.append(copy.deepcopy(entry))
                count += 1
                if timestamp(entry.get('start')) <= now < timestamp(entry.get('stop')):
                    if channel_id not in current:
                        current.append(channel_id)
        if not count:
            raise ValueError(f'{name}: no usable programmes; no guides published')
        report['playlists'][name] = {
            'total_channels': len(wanted), 'channels_with_programmes': len(covered),
            'channels_with_current_programme': len(current), 'programmes': count,
            'covered': covered, 'retained_from_previous_run': retained, 'missing': missing,
        }
        outputs[outdir / f'{name}.xml'] = ET.tostring(tv, encoding='utf-8', xml_declaration=True)
        print(f'{name}: {len(covered)}/{len(wanted)} channels, {count} programmes; {len(retained)} retained')
    # Validate every output before replacing any published file.
    for path, content in outputs.items():
        temp = path.with_suffix('.xml.tmp')
        temp.write_bytes(content)
        temp.replace(path)
    (outdir / 'status.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', type=Path)
    group.add_argument('--publish', type=Path)
    args = parser.parse_args()
    if args.prepare:
        prepare(args.prepare)
    else:
        publish(args.publish)
