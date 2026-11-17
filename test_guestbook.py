import os
import tempfile
import unittest

from guestbook import entry, sign, signatures


class GuestbookTest(unittest.TestCase):
    def test_an_entry_is_the_day_then_the_name_on_one_line(self):
        self.assertEqual(entry("  a third\nkeeper ", "2026-11-06"), "2026-11-06 · a third keeper")

    def test_signatures_are_kept_oldest_first(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "guestbook.txt")
            self.assertEqual(signatures(path), [])
            sign(path, "Alice", "2026-11-06")
            sign(path, "Bob", "2026-11-07")
            self.assertEqual(signatures(path), ["2026-11-06 · Alice", "2026-11-07 · Bob"])


if __name__ == "__main__":
    unittest.main()
