"""look for requirements.txt files and check for updates"""

import json
import re
import urllib.request
from pathlib import Path


class RequirementsCheck:
    """handle version check for requirements"""

    SEARCH = "requirements*.txt"
    PATTERN = r'^\s*([a-zA-Z0-9_\-]+)(\[[^\]]+\])?\s*==\s*([0-9]+(?:\.[0-9]+){0,2})\s*$'
    IGNORE = ["__pycache__", ".venv"]

    def update(self) -> None:
        """entry point, check for updates"""
        requirements_files = self.find_requirements()
        if not requirements_files:
            print(f"no {self.SEARCH} files found in cwd")
            return

        for requirements_file in requirements_files:
            print(f"checking: {requirements_file}")
            self.parse_file(requirements_file)

    def find_requirements(self) -> list[Path]:
        """find all requirement files"""
        cwd = Path.cwd()
        requirements_files = [
            file for file in cwd.rglob(self.SEARCH)
            if not any(exclude_dir in file.parts for exclude_dir in self.IGNORE)
        ]

        return requirements_files

    def parse_file(self, requirements_file: Path):
        """parse single file"""
        with open(requirements_file, "r", encoding="utf-8") as f:
            requirement_lines = [i.strip() for i in f.readlines()]

        new_requirement_lines = []

        for requirement_line in requirement_lines:
            match = re.match(self.PATTERN, requirement_line)
            if not match:
                new_requirement_lines.append(requirement_line)
                continue

            package, _, version_local = match.groups()
            package_info = self.get_package_info(package)
            new_version = self.compare_version(version_local, package_info)
            if new_version:
                new_requirement_lines.append(f"{package}=={new_version}")
                continue

            new_requirement_lines.append(requirement_line)

        to_update = sorted(new_requirement_lines, key=lambda s: s.lower())
        if to_update == requirement_lines:
            print("nothing to update")
            return

        self.update_requirements(requirements_file, to_update)

    def get_package_info(self, package: str) -> dict[str,str]:
        """get remote version of package"""
        url = f"https://pypi.org/pypi/{package}/json"
        with urllib.request.urlopen(url) as url:
            response = json.load(url)

        info = response["info"]
        package_info = {
            "package": package,
            "homepage": info["home_page"] or info["package_url"],
            "version_remote": info["version"],
        }

        return package_info

    def compare_version(self, version_local: str, package_info: dict) -> str | None:
        """compare and update versions"""
        if version_local == package_info["version_remote"]:
            return None

        message = (
            f"Update found for: {package_info['package']}\n"
            + f"{version_local} ==> {package_info['version_remote']}\n"
            + package_info["homepage"]
        )
        print(message)
        input_response = input("\napply? [y/n]\n")

        if input_response.strip().lower() == "y":
            return package_info["version_remote"]

        return None

    def update_requirements(self, requirements_file: Path, to_update: list[str]) -> None:
        """write back"""
        with open(requirements_file, "w", encoding="utf-8") as f:
            f.writelines([f"{i}\n" for i in to_update])


def main():
    """main for CLI"""
    RequirementsCheck().update()


if __name__ == "__main__":
    main()
