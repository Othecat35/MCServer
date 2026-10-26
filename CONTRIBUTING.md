# License

By submitting a pull request, you agree that your contribution is licensed under the MIT License.

# Development

- Python >= 3.12 (3.14 is recommended)
- Install with `pip install -e .`
- Use `ruff format` to reformat code

# Release

1. Bump version in `src/mcserver/__init__.py`
2. `python zip_app.py`
3. Tag: `git tag vX.Y.Z && git push --tags`
4. Create GitHub release, attach `dist/mcserver`
