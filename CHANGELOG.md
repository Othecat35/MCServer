# Semantic Versioning (MAJOR.minor._patch_):
- MAJOR: When you make incompatible changes
- minor: When you add or change functionality that is backward compatible
- _patch_: When you make backward compatible bug fixes

# The "v" Version Prefix:
- Use in:
  - Git Tag
  - Github Release
  - `mcserver --version`
  - User Agent
  - (Basically everything that a user will see)
- Don't use in:
  - Internal script version (`__version__`)
  - Changelog header
  - (Basically everything that is internal about the project)

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
- New command `D`

### Changed
- Command `A` now print `Hello, world!`

### Deprecating
- Removing command `C`

### Removed
- Command `B`

### Fixed
- Bug where the script stuck in an infinite loop

### Security
- Fix auth bug

[unreleased] : https://github.com/Othecat35/MCServer/compare/<latest_tag>...HEAD
[<current_tag>] : https://github.com/Othecat35/MCServer/compare/<prev_tag>...<current_tag>

```

---

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

[unreleased] : https://github.com/Othecat35/MCServer/compare/1.11.9...HEAD
