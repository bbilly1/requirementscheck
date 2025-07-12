"""package setup"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="RequirementsCheck",
    version="0.1.0",
    author="Simon",
    author_email="simobilleter@gmail.com",
    description="A CLI utility to check and update Python package versions in requirements.txt files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bbilly1/requirementscheck",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["packaging"],
    entry_points={
        "console_scripts": [
            "requirementscheck=requirementscheck.requirementscheck:main",
        ],
    },
)
