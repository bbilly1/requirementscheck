# Version Check

Core Functionality:
- Look for requirements*.txt files in your working directory and check for updates.
- Prompt to confirm each update with an upstream url.

## Install

RequirementsCheck is available on [pypi.org/project/RequirementsCheck/](https://pypi.org/project/RequirementsCheck/). Install into your environment with pip:

```
pip install requirementscheck
```

Add it to your `requirements.txt` file, pin the release, and use requirementscheck to update requirementscheck in your `requirements.txt` file.

## Run

From your Python project root folder run:
```
requirementscheck
```

to look for requirements files and update your dependencies based on your prompts.

Additionally, this takes to optional arguments:

- `--confirm | --no-confirm`: Ask for confirmation with link to upstream package before applying update, default `True`.
- `--pin | --no-pin`: Pin a dependency to the latest version if found to be not pinned, default `False`.
- `-h | --help`: Print help text and exit.

## Ignore

You can ignore certain lines in your requirements file by appending a comment `# rc:ignore` to the line, indicating for requirementscheck to ignore that line.

## Build

Run tests:
```
python -m unittest src/requirementscheck/test_requirementscheck.py
```

1. Update the version in setup.py
2. Git Tag
3. Push tag
4. Create release on GH
5. Build and update package to pypi:

    ```bash
    python -m build
    python -m twine upload dist/*
    ```

## Additional
Newest docs on GitHub: [bbilly1/requirementscheck](https://github.com/bbilly1/requirementscheck).
