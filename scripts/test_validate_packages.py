#!/usr/bin/env python3
"""
Unit tests for validate_packages.py helper functions.

Run with:  python3 -m pytest scripts/test_validate_packages.py -v
       or: python3 scripts/test_validate_packages.py
"""

import os
import stat
import sys
import tempfile
import unittest

# Allow importing from the same directory
sys.path.insert(0, os.path.dirname(__file__))
from validate_packages import (
    _is_executable,
    validate_manifest_fields,
    validate_modules_contract,
)


class TestIsExecutable(unittest.TestCase):
    def test_executable_file_returns_true(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            os.chmod(path, stat.S_IRWXU)
            self.assertTrue(_is_executable(path))
        finally:
            os.unlink(path)

    def test_non_executable_file_returns_false(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
            self.assertFalse(_is_executable(path))
        finally:
            os.unlink(path)

    def test_missing_file_returns_false(self):
        self.assertFalse(_is_executable("/nonexistent/path/script"))


class TestValidateManifestFields(unittest.TestCase):
    def _full_manifest(self):
        return {
            "name": "my-pkg",
            "version": "1.0.0",
            "description": "A package",
            "author": "Dev",
            "license": "MIT",
            "requirements": {"cockpit": ">=0.1.0"},
        }

    def test_valid_manifest_no_errors(self):
        self.assertEqual(validate_manifest_fields("my-pkg", self._full_manifest()), 0)

    def test_missing_name_reports_error(self):
        m = self._full_manifest()
        del m["name"]
        self.assertGreater(validate_manifest_fields("my-pkg", m), 0)

    def test_missing_description_reports_error(self):
        m = self._full_manifest()
        del m["description"]
        self.assertGreater(validate_manifest_fields("my-pkg", m), 0)

    def test_missing_author_reports_error(self):
        m = self._full_manifest()
        del m["author"]
        self.assertGreater(validate_manifest_fields("my-pkg", m), 0)

    def test_missing_license_reports_error(self):
        m = self._full_manifest()
        del m["license"]
        self.assertGreater(validate_manifest_fields("my-pkg", m), 0)

    def test_missing_requirements_cockpit_reports_error(self):
        m = self._full_manifest()
        del m["requirements"]
        self.assertGreater(validate_manifest_fields("my-pkg", m), 0)

    def test_requirements_without_cockpit_key_reports_error(self):
        m = self._full_manifest()
        m["requirements"] = {"other": "1.0"}
        self.assertGreater(validate_manifest_fields("my-pkg", m), 0)

    def test_multiple_missing_fields_counts_all(self):
        errors = validate_manifest_fields("my-pkg", {})
        # name, version, description, author, license + requirements.cockpit = 6
        self.assertEqual(errors, 6)


class TestValidateModulesContract(unittest.TestCase):
    def _make_pkg_dir(self, with_configure=True, with_validate=True, executable=True):
        """Create a temp package dir with optional bin/ scripts."""
        tmpdir = tempfile.mkdtemp()
        bin_dir = os.path.join(tmpdir, "bin")
        os.makedirs(bin_dir)
        perm = stat.S_IRWXU if executable else (stat.S_IRUSR | stat.S_IWUSR)
        if with_configure:
            p = os.path.join(bin_dir, "configure")
            open(p, "w").close()
            os.chmod(p, perm)
        if with_validate:
            p = os.path.join(bin_dir, "validate")
            open(p, "w").close()
            os.chmod(p, perm)
        return tmpdir

    def _cleanup(self, path):
        import shutil
        shutil.rmtree(path, ignore_errors=True)

    def test_no_modules_feature_skips_check(self):
        manifest = {"features": {"kb": [{"path": "kb/doc.md"}]}}
        tmpdir = self._make_pkg_dir(with_configure=False, with_validate=False)
        try:
            self.assertEqual(validate_modules_contract("pkg", tmpdir, manifest), 0)
        finally:
            self._cleanup(tmpdir)

    def test_empty_features_skips_check(self):
        manifest = {"features": {}}
        tmpdir = self._make_pkg_dir(with_configure=False, with_validate=False)
        try:
            self.assertEqual(validate_modules_contract("pkg", tmpdir, manifest), 0)
        finally:
            self._cleanup(tmpdir)

    def test_no_features_key_skips_check(self):
        manifest = {}
        tmpdir = self._make_pkg_dir(with_configure=False, with_validate=False)
        try:
            self.assertEqual(validate_modules_contract("pkg", tmpdir, manifest), 0)
        finally:
            self._cleanup(tmpdir)

    def test_modules_with_both_scripts_ok(self):
        manifest = {"features": {"modules": [{"path": "bin/cmd"}]}}
        tmpdir = self._make_pkg_dir()
        try:
            self.assertEqual(validate_modules_contract("pkg", tmpdir, manifest), 0)
        finally:
            self._cleanup(tmpdir)

    def test_modules_missing_configure_reports_error(self):
        manifest = {"features": {"modules": [{"path": "bin/cmd"}]}}
        tmpdir = self._make_pkg_dir(with_configure=False)
        try:
            errors = validate_modules_contract("pkg", tmpdir, manifest)
            self.assertGreater(errors, 0)
        finally:
            self._cleanup(tmpdir)

    def test_modules_missing_validate_reports_error(self):
        manifest = {"features": {"modules": [{"path": "bin/cmd"}]}}
        tmpdir = self._make_pkg_dir(with_validate=False)
        try:
            errors = validate_modules_contract("pkg", tmpdir, manifest)
            self.assertGreater(errors, 0)
        finally:
            self._cleanup(tmpdir)

    def test_modules_both_missing_reports_two_errors(self):
        manifest = {"features": {"modules": [{"path": "bin/cmd"}]}}
        tmpdir = self._make_pkg_dir(with_configure=False, with_validate=False)
        try:
            self.assertEqual(validate_modules_contract("pkg", tmpdir, manifest), 2)
        finally:
            self._cleanup(tmpdir)

    def test_modules_non_executable_configure_reports_error(self):
        manifest = {"features": {"modules": [{"path": "bin/cmd"}]}}
        tmpdir = self._make_pkg_dir(executable=False)
        try:
            errors = validate_modules_contract("pkg", tmpdir, manifest)
            self.assertGreater(errors, 0)
        finally:
            self._cleanup(tmpdir)


if __name__ == "__main__":
    unittest.main()
