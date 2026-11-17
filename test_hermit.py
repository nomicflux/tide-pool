import unittest
from xml.etree import ElementTree as ET

from hermit import portrait


class HermitTest(unittest.TestCase):
    def test_the_house_and_line_are_safe_visible_text(self):
        root = ET.fromstring(portrait('<lamp>', '<lamp> & a window'))
        text = ' '.join(root.itertext())
        self.assertIn('House: <lamp>', text)
        self.assertIn('<lamp> & a window', text)

    def test_a_long_address_fits_below_the_crab(self):
        line = 'the sea keeps a room for every returning keeper ' * 8
        root = ET.fromstring(portrait('water', line))
        rows = root.findall('{*}g/{*}text')
        self.assertEqual(' '.join(' '.join(row.itertext()) for row in rows[2:]).split(), line.split())
        self.assertLess(float(rows[-1].attrib['y']), float(root.attrib['height']))


if __name__ == '__main__':
    unittest.main()
