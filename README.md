# Version Check

Core Functionality:
- Look for requirements*.txt files in your working directory and check for updates.
- Prompt to confirm each update with an upstream url.

## Install

Install into your environment with pip:

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

## Build

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
