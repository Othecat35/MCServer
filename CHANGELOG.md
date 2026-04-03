# Semantic Versioning (MAJOR.minor._patch_):
- MAJOR: When you introduce breaking changes (Rename a configuration file, rename directory, etc)
- minor: When you add/change the functionality from user perspective (Add new command, add new stuff like dependency resolution, etc)
- _patch_: When you change internal code without visible changes (Fix a typo, rework an algorithm, etc)

# The "v" Version Prefix:
- Use in:
  - Git Tag
  - Github Release
  - `mcserver --version`
  - User Agent
  - (Basically everything that a user will saw)
- Don't use in:
  - Internal script version (`__version__`)
  - Changelog header
  - Version comparing logic
  - (Basically everything that is just internal about the project)

# Changelog Structure (Examples):
```md
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Mod indexing

### Removed

- The whole project

## [<semver>] - <date(yyyy/MM/dd)>

### Added

- A new command A

### Changed

- Behaviour of command A

### Deprecating

- Removing command C

### Removed

- Removed command B

### Fixed

- Bug where tge script in a infinite loop

### Security

- Fix auth bug in the script

...

[<semver](https://github.com/Othecat35/MCServer/compare/<prev_tag>...<current_tag>)

```

---
