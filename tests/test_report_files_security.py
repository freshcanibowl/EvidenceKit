"""Local-only security checks. No model, Gradio or network required."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from open_evidencekit import report_files


class ReportLifetimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.path_patch = patch.object(report_files, 'report_dir', return_value=self.base)
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

    def test_save_is_private_and_valid_json(self):
        p = Path(report_files.save_report({'verdict': 'INSUFFICIENT_EVIDENCE'}))
        self.assertEqual(p.parent, self.base)
        self.assertIn('INSUFFICIENT_EVIDENCE', p.read_text())
        if os.name == 'posix':
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)

    def test_expired_is_removed_recent_is_kept(self):
        old = Path(report_files.save_report({'id': 'old'}))
        recent = Path(report_files.save_report({'id': 'new'}))
        os.utime(old, (100, 100))
        os.utime(recent, (4000, 4000))
        self.assertEqual(report_files.cleanup_expired(now=4000), 1)
        self.assertFalse(old.exists())
        self.assertTrue(recent.exists())

    def test_unrelated_file_preserved(self):
        p = self.base / 'user-data.json'
        p.write_text('keep')
        os.utime(p, (100, 100))
        report_files.cleanup_expired(now=4000)
        self.assertTrue(p.exists())

    def test_symlink_not_followed_or_deleted(self):
        target = self.base / 'outside.txt'
        target.write_text('keep')
        link = self.base / 'evidencekit-report-fake.json'
        try: link.symlink_to(target)
        except (OSError, NotImplementedError): self.skipTest('Symlinks unavailable')
        report_files.cleanup_expired(now=9999999)
        self.assertTrue(link.is_symlink())
        self.assertEqual(target.read_text(), 'keep')

    def test_excessively_large_report_rejected(self):
        with self.assertRaises(ValueError):
            report_files.save_report({'payload': 'a' * (report_files.MAX_REPORT_BYTES + 1)})


if __name__ == '__main__':
    unittest.main()
