# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-06-14

### Changed

- Separate the project index data to metadata and relationship

### Fixed

- Fetching list of ids when it is not needed

## [1.13.16] - 2026-06-11

### Fixed

- An unknown bug

## [1.13.15] - 2026-06-11

### Added

- Error class when there's no file in a project version

### Fixed

- The slug_to_id function to use existing format
- The Mdorinth API base to use https instead of http

### Removed

- Unused error class

## [1.13.14] - 2026-06-11

### Changed

- Revert code changes

## [1.13.13] - 2026-06-11

### Changed

- Code

## [1.13.12] - 2026-06-05

### Changed

- Refactor some code

## [1.13.11] - 2026-05-29

### Changed

- Code structure to be modula with zipapp
- Rename project index directory to `project_indexes`

### Fixed

- Error class name inconsistency

## [1.13.10] - 2026-05-16

### Fixed

- Missing `mods` directory when adding mod
- Crash when using `--no-filter` option on `search`
- Invalid code in an error

## [1.13.9] - 2026-05-11

### Added

- Error message for adding projects that doesn't have version for current server

### Fixed

- Error when adding project (invalid value)

## [1.13.8] - 2026-04-29

### Fixed

- Revert Modrinth API base URL

## [1.13.7] - 2026-04-29

### Added

- Code type hinting
- `fetch_project_versions` is more close to Mdorinth docs

### Fixed

- The width of the wrapped text always be 80, now it is terminal width

## [1.13.6] - 2026-04-27

### Added

- Check to make sure only adding slug -> id for required and incompatible only

### Changed

- Some commands description in help

### Fixed

- Remove unused data in an error message

## [1.13.5] - 2026-04-25

### Fixed

- Crash when searching project in a vanilla/no config setup

## [1.13.4] - 2026-04-25

### Fixed

- Why so many bug fixes?

## [1.13.3] - 2026-04-25

### Fixed

- The previous bug again

## [1.13.2] - 2026-04-25

### Fixed

- Error name not reflecting changes

## [1.13.1] - 2026-04-25

### Fixed

- It now doesn't try to make mods/ or projects/ directory for "vanilla" server

## [1.13.0] - 2026-04-24

### Added

- Preparing to support plugins
- Slug to ID cache, reducing API call

### Changed

- EULA agreement sentence
- Improved confirmation prompt

## [1.12.2] - 2026-04-14

### Fixed

- Revert Modrinth API URL back to normal

## [1.12.1] - 2026-04-14

### Added

- Create `mods_index` directory when running `init`

## [1.12.0] - 2026-04-14

### Added

- Mod indexing functionality

### Changed

- Better mod conflict error
- Faster mod resolving

[unreleased]: https://github.com/Othecat35/MCServer/compare/v1.13.16...HEAD
[1.13.16]: https://github.com/Othecat35/MCServer/compare/v1.13.15...v1.13.16
[1.13.15]: https://github.com/Othecat35/MCServer/compare/v1.13.14...v1.13.15
[1.13.14]: https://github.com/Othecat35/MCServer/compare/v1.13.13...v1.13.14
[1.13.13]: https://github.com/Othecat35/MCServer/compare/v1.13.12...v1.13.13
[1.13.12]: https://github.com/Othecat35/MCServer/compare/v1.13.11...v1.13.12
[1.13.11]: https://github.com/Othecat35/MCServer/compare/v1.13.10...v1.13.11
[1.13.10]: https://github.com/Othecat35/MCServer/compare/v1.13.9...v1.13.10
[1.13.9]: https://github.com/Othecat35/MCServer/compare/v1.13.8...v1.13.9
[1.13.8]: https://github.com/Othecat35/MCServer/compare/v1.13.7...v1.13.8
[1.13.7]: https://github.com/Othecat35/MCServer/compare/v1.13.6...v1.13.7
[1.13.6]: https://github.com/Othecat35/MCServer/compare/v1.13.5...v1.13.6
[1.13.5]: https://github.com/Othecat35/MCServer/compare/v1.13.4...v1.13.5
[1.13.4]: https://github.com/Othecat35/MCServer/compare/v1.13.3...v1.13.4
[1.13.3]: https://github.com/Othecat35/MCServer/compare/v1.13.2...v1.13.3
[1.13.2]: https://github.com/Othecat35/MCServer/compare/v1.13.1...v1.13.2
[1.13.1]: https://github.com/Othecat35/MCServer/compare/v1.13.0...v1.13.1
[1.13.0]: https://github.com/Othecat35/MCServer/compare/v1.12.2...v1.13.0
[1.12.2]: https://github.com/Othecat35/MCServer/compare/v1.12.1...v1.12.2
[1.12.1]: https://github.com/Othecat35/MCServer/compare/v1.12.0...v1.12.1
[1.12.0]: https://github.com/Othecat35/MCServer/compare/v1.11.8...v1.12.0
