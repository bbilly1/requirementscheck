"""tests"""

# pylint: disable=protected-access

import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from src.requirementscheck.requirementscheck import RequirementsCheck


class TestRequirementsCheck(unittest.TestCase):
    """all test cases"""

    @patch("src.requirementscheck.requirementscheck.Path.rglob")
    def test_find_requirements(self, mock_rglob):
        """Test finding requirements files."""
        mock_rglob.return_value = [
            Path("requirements.txt"),
            Path("__pycache__/requirements.txt"),
        ]
        checker = RequirementsCheck(confirm=False, pin_requirement=False)
        found_files = checker._find_requirements()
        self.assertIn(Path("requirements.txt"), found_files)
        self.assertNotIn(Path("__pycache__/requirements.txt"), found_files)

    @patch("builtins.open", new_callable=mock_open, read_data="package_name==1.0.0\n")
    @patch("src.requirementscheck.requirementscheck.RequirementsCheck.get_package_info")
    def test_parse_file(self, mock_get_package_info, mocked_open):  # pylint: disable=unused-argument
        """Test parsing and updating a requirements file."""
        mock_get_package_info.return_value = {
            "package": "package_name",
            "homepage": "https://pypi.org/project/package_name",
            "version_remote": "2.0.0",
        }
        checker = RequirementsCheck(confirm=False, pin_requirement=False)
        with patch.object(checker, "update_requirements") as mock_update:
            checker.parse_file(Path("requirements.txt"))
            mock_update.assert_called_once()
            updated_lines = mock_update.call_args[0][1]
            self.assertIn("package_name==2.0.0", updated_lines)

    @patch("src.requirementscheck.requirementscheck.urllib.request.urlopen")
    def test_get_package_info(self, mock_urlopen):
        """Test fetching package info from PyPI."""
        mock_urlopen.return_value.__enter__.return_value.read.return_value = (
            b'{"info": {"home_page": "https://pypi.org/project/testpkg", "version": "1.2.3"}}'
        )
        checker = RequirementsCheck(confirm=False, pin_requirement=False)
        package_info = checker.get_package_info("testpkg")
        self.assertEqual(package_info["package"], "testpkg")
        self.assertEqual(package_info["version_remote"], "1.2.3")
        self.assertEqual(package_info["homepage"], "https://pypi.org/project/testpkg")

    @patch("builtins.input", return_value="y")
    def test_compare_version_confirm(self, mock_input):  # pylint: disable=unused-argument
        """Test confirming version update."""
        checker = RequirementsCheck(confirm=True, pin_requirement=False)
        package_info = {
            "package": "testpkg",
            "homepage": "https://pypi.org/project/testpkg",
            "version_remote": "1.2.3",
        }
        new_version = checker._compare_version("1.0.0", package_info)
        self.assertEqual(new_version, "1.2.3")

    def test_compare_version_no_update(self):
        """Test no update needed when versions match."""
        checker = RequirementsCheck(confirm=False, pin_requirement=False)
        package_info = {
            "package": "testpkg",
            "homepage": "https://pypi.org/project/testpkg",
            "version_remote": "1.0.0",
        }
        new_version = checker._compare_version("1.0.0", package_info)
        self.assertIsNone(new_version)

    @patch("builtins.input", return_value="n")
    def test_compare_version_decline_update(self, mock_input):  # pylint: disable=unused-argument
        """Test declining version update."""
        checker = RequirementsCheck(confirm=True, pin_requirement=False)
        package_info = {
            "package": "testpkg",
            "homepage": "https://pypi.org/project/testpkg",
            "version_remote": "1.2.3",
        }
        new_version = checker._compare_version("1.0.0", package_info)
        self.assertIsNone(new_version)

    @patch("builtins.open", new_callable=mock_open, read_data="testpkg\n")
    @patch("src.requirementscheck.requirementscheck.RequirementsCheck.get_package_info")
    def test_pin_unpinned_requirement(self, mock_get_package_info, mocked_open):  # pylint: disable=unused-argument
        """Test pinning unpinned requirements."""
        mock_get_package_info.return_value = {
            "package": "testpkg",
            "homepage": "https://pypi.org/project/testpkg",
            "version_remote": "1.2.3",
        }
        checker = RequirementsCheck(confirm=False, pin_requirement=True)
        with patch.object(checker, "update_requirements") as mock_update:
            checker.parse_file(Path("requirements.txt"))
            mock_update.assert_called_once()
            updated_lines = mock_update.call_args[0][1]
            self.assertIn("testpkg==1.2.3", updated_lines)

    @patch("builtins.open", new_callable=mock_open, read_data="package_name==1.0.0\n")
    @patch("src.requirementscheck.requirementscheck.RequirementsCheck.get_package_info")
    def test_no_changes_to_requirements(self, mock_get_package_info, mocked_open):  # pylint: disable=unused-argument
        """Test when no changes are needed."""
        mock_get_package_info.return_value = {
            "package": "package_name",
            "homepage": "https://pypi.org/project/package_name",
            "version_remote": "1.0.0",
        }
        checker = RequirementsCheck(confirm=False, pin_requirement=False)
        with patch.object(checker, "update_requirements") as mock_update:
            checker.parse_file(Path("requirements.txt"))
            mock_update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
