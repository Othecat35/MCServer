# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New directory mods_index under .mcserver
- Mod indexing related function (write, read, create, update)
- `add_mod` now write mod index

### Changed
- `merge_dict` now return a new dictionary instead of modifying the input
- `add_mod` now use `while required_mod_id`
- Rename output data of `fetch_mod_version`
- Rewrite some code in `resolve_mods`
- `resolve_mods` now compare to the past

### Removed
- Redundant "or mod is manual" in `resolve_mods` because manual mod is always start wity "required" type
- Redundant "or mod is manual" in mod type bucket in `add_mod`

[unreleased] : https://github.com/Othecat35/MCServer/compare/1.11.9...HEAD
