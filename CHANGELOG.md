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

### Added
- Variable `mod_index_dir`
- Type hinting to functions parameter
- Homepage to `show` output
- `search`'s `--sort-by (-s)` default to `relevance`
- `headers` in returned data from `fetch_url`
- "this" = "these" special plural

### Changed
- Rename variable `modrinth_api` to `modrinth_api_base`
- Rename function `color_string` to `wrap_ansi`
- `merge_dict` now don't skip `None` values
- Change the `User-Agent` to `Othecat35/MCServer/{__version__}` (like what Modrinth suggest)
- Move the response data to `text` as dictionary for `headers` in `fetch_url`
- Rename variable `request_url` to `request` in `fetch_url`
- Updated `fetch_url` debug message
- Removed restriction that `print_status` doesn't work in debug mode
- `resolved_mods` is reworked

### Fixed
- Typo variable name in `add_mod`, `mod_dependencies_types` should be `mod_dependency_types`

[unreleased] : https://github.com/Othecat35/MCServer/compare/1.11.8...HEAD
