import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

spec = importlib.util.spec_from_file_location('epg', Path(__file__).resolve().parents[1] / 'scripts/epg.py')
epg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(epg)


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original = epg.ROOT
        epg.ROOT = self.root
        self.addCleanup(setattr, epg, 'ROOT', self.original)
        (self.root / 'config').mkdir()
        (self.root / 'epg').mkdir()
        self.now = datetime.now(timezone.utc)
        for name in epg.PLAYLISTS:
            (self.root / 'config' / f'{name}.json').write_text(json.dumps([
                {'tvg_id': 'Test.us@East', 'name': 'Test'},
                {'tvg_id': 'Other.us@SD', 'name': 'Other'},
            ]))

    def write_guide(self, path, rows):
        tv = ET.Element('tv')
        for channel, start, stop, title in rows:
            p = ET.SubElement(tv, 'programme', channel=channel,
                start=(self.now + timedelta(hours=start)).strftime('%Y%m%d%H%M%S +0000'),
                stop=(self.now + timedelta(hours=stop)).strftime('%Y%m%d%H%M%S +0000'))
            ET.SubElement(p, 'title').text = title
        ET.ElementTree(tv).write(path, encoding='utf-8', xml_declaration=True)

    def test_feed_identity_deduplication_expiry_and_retention(self):
        for name in epg.PLAYLISTS:
            self.write_guide(self.root / 'epg' / f'{name}.xml', [
                ('Other.us@SD', -1, 1, 'Retained'),
                ('Other.us@SD', -4, -3, 'Expired'),
            ])
        source = self.root / 'source.xml'
        self.write_guide(source, [
            ('Test.us@East', -1, 1, 'A & B'),
            ('Test.us@East', -1, 1, 'A & B'),
            ('Test.us@West', -1, 1, 'Wrong feed'),
            ('Test.us@East', -4, -3, 'Expired'),
            ('Test.us@East', 2, 1, 'Invalid duration'),
        ])
        epg.publish(source)
        for name in epg.PLAYLISTS:
            programs = ET.parse(self.root / 'epg' / f'{name}.xml').getroot().findall('programme')
            self.assertEqual([p.findtext('title') for p in programs], ['A & B', 'Retained'])
        status = json.loads((self.root / 'epg/status.json').read_text())
        self.assertEqual(status['playlists']['sports']['retained_from_previous_run'], ['Other.us@SD'])

    def test_empty_fetch_leaves_existing_files_untouched(self):
        original = b'<tv></tv>'
        target = self.root / 'epg/mexico.xml'
        target.write_bytes(original)
        source = self.root / 'empty.xml'
        source.write_bytes(original)
        with self.assertRaises(ValueError):
            epg.publish(source)
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse((self.root / 'epg/status.json').exists())

    def test_timezone_offset(self):
        self.assertEqual(epg.timestamp('20260923120000 -0600'), epg.timestamp('20260923180000 +0000'))
        with self.assertRaises(ValueError):
            epg.timestamp('20260923120000')


if __name__ == '__main__':
    unittest.main()
