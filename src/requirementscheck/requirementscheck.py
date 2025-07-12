"""look for requirements.txt files and check for updates"""

import argparse
import json
import re
import urllib.request
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


class RequirementsCheck:
    """handle version check for requirements"""

    SEARCH = "requirements*.txt"
    IGNORE = ["__pycache__", ".venv"]

    def __init__(self, confirm: bool, pin_requirement: bool):
        self.confirm = confirm
        self.pin_requirement = pin_requirement

    def update(self) -> None:
        """entry point, check for updates"""
        requirements_files = self._find_requirements()
        if not requirements_files:
            print(f"no {self.SEARCH} files found in cwd")
            return

        for requirements_file in requirements_files:
            print(f"checking: {requirements_file}")
            self.parse_file(requirements_file)

    def _find_requirements(self) -> list[Path]:
        """find all requirement files"""
        cwd = Path.cwd()
        requirements_files = [
            file for file in cwd.rglob(self.SEARCH) if not any(exclude_dir in file.parts for exclude_dir in self.IGNORE)
        ]

        return requirements_files

    def parse_file(self, requirements_file: Path) -> None:
        """parse the file"""
        with open(requirements_file, "r", encoding="utf-8") as f:
            requirement_lines = [i.strip() for i in f.readlines()]

        lines_parsed = []
        for line in requirement_lines:
            if not line or line[0] in ["#", "-"] or "# rc:ignore" in line:
                lines_parsed.append(line)
                continue

            try:
                requirement, extra_args = self._split_requirement(line)
                req = Requirement(requirement)

                if self.pin_requirement and not req.specifier:
                    pinned_req = self._add_req_pin(req)
                    lines_parsed.append(f"{pinned_req} {extra_args}".strip())
                elif not self.pin_requirement and req.specifier:
                    updated_req = self._update_line(req)
                    lines_parsed.append(f"{updated_req} {extra_args}".strip())
                else:
                    lines_parsed.append(line)

            except Exception as err:  # pylint: disable=broad-exception-caught
                print(f"Skipping line failed to parse: {line}, {err}")
                lines_parsed.append(line)

        to_update = sorted(lines_parsed, key=lambda s: s.lower())
        if to_update == requirement_lines:
            print("nothing to update")
            return

        self.update_requirements(requirements_file, to_update)

    def _split_requirement(self, line: str) -> tuple[str, str]:
        """Splits the package requirement from any extra pip arguments."""
        parts = re.split(r"\s(--\S+)", line, maxsplit=1)
        requirement = parts[0].strip()  # Package requirement
        extra_args = "".join(parts[1:]).strip() if len(parts) > 1 else ""  # Remaining pip options
        return requirement, extra_args

    def _update_line(self, req: Requirement) -> Requirement:
        """update line"""
        updated_specifiers = []
        for specifier in req.specifier:
            if specifier.operator == "==":
                version_local = specifier.version
                package_info = self.get_package_info(req.name)
                new_version = self._compare_version(version_local, package_info)
                if new_version:
                    updated_specifiers.append(f"=={new_version}")
                else:
                    updated_specifiers.append(f"=={version_local}")

        req.specifier = SpecifierSet(",".join(updated_specifiers))
        return req

    def _add_req_pin(self, req: Requirement) -> Requirement:
        """pin requirement without specifier"""
        package_info = self.get_package_info(req.name)
        version_remote = package_info["version_remote"]
        if self.confirm:
            print(f"\npin package '{req.name}' to version {version_remote}")
            input_response = input("\napply? [Y/n]\n") or "y"
            if input_response.strip().lower() == "y":
                req.specifier = SpecifierSet(f"=={version_remote}")
        else:
            req.specifier = SpecifierSet(f"=={version_remote}")

        return req

    def get_package_info(self, package: str) -> dict[str, str]:
        """get remote version of package"""
        url = f"https://pypi.org/pypi/{package}/json"
        with urllib.request.urlopen(url) as urllib_response:
            response = json.load(urllib_response)

        info = response["info"]
        package_info = {
            "package": package,
            "homepage": info["home_page"] or info["package_url"],
            "version_remote": info["version"],
        }

        return package_info

    def _compare_version(self, version_local: str, package_info: dict) -> str | None:
        """compare and update versions"""
        if version_local == package_info["version_remote"]:
            return None

        message = (
            f"\nUpdate found for: {package_info['package']}\n"
            + f"{version_local} ==> {package_info['version_remote']}\n"
            + package_info["homepage"]
        )
        print(message)
        if self.confirm:
            input_response = input("\napply? [Y/n]\n") or "y"
            if input_response.strip().lower() == "y":
                return package_info["version_remote"]

            return None

        return package_info["version_remote"]

    def update_requirements(self, requirements_file: Path, to_update: list[str]) -> None:
        """write back"""
        with open(requirements_file, "w", encoding="utf-8") as f:
            f.writelines([f"{i}\n" for i in to_update])


def main():
    """main for CLI"""
    parser = argparse.ArgumentParser(
        description="A CLI utility to check and update Python package versions in requirements.txt files"
    )
    parser.add_argument(
        "--confirm", help="Prompt to confirm update", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument("--pin", help="Pin unpinned requirements", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    RequirementsCheck(confirm=args.confirm, pin_requirement=args.pin).update()


if __name__ == "__main__":
    main()
