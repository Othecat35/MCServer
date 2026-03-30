# v1.0.0 - First release
Added:
 - `init` command
 - `search` command
 - `start` command
 - Config system

# v1.0.1 - Update log messages
Changes:
 - `Searching mods` message now includes search filters
 - Remove the word `file` in  is some configuration error messages

# v1.1.0 - Show command
Added:
 - `show` command

# 1.1.1
- Replace textwrap.shorten to .wrap in `search` mod description

# 1.2.0
- Move java command options to a sepsrate launcher.json configuration

# 1.2.1
- Renamed function color_string to color_text
- Replace all raise error type with Exception
- Update "Showing ... out of ... mods ..." message to have pages count
- Update mod_environment_color to use color_text

1.3.1
- Renamed "subcommand" to "command"
- Added function "request_download"
- Added "install" command
- Added new subdirectory "tempfiles"
- Replace "User-Agent" with variable "user_agent"

1.4.0
- Update request_download to use a variable for the temporary file
- Renamed (server.json).software.loader to .name
- Renamed (server.json).software to .loader
- Added a log in the `install` command about what going to be downloaded
- Add check if server is vanilla in `search`

1.4.1
- Make the "Let it crash" depends on MCSERVER_DEBUG=1

1.4.2
- EULA agreement consent?

1.4.3
- Change 'Showing ... mods' from using 'search_limit' to 'shown_mods_count'

1.5.0
- Added option '--no-filter' to 'search' mod without version-dependent filter

1.5.1
- Added fallback value for mod_environment_color()
- Added error message rewrites for config_generate, config_load
- Added function to wrap text to current terminal size
- Rename 'id' to 'mod_id' in show_mods() command
- Replace bare Exception to EULAAgreementError in start_server()

1.5.2
- Make the "title (slug) by author" using wrap_text

1.6.0
- Added 'add' command
- Fixes typo on generate_config
- 'User-Agent' now include script version
- Added 'Temporary File' debug message in request_download
- Added 2 new class for error
- Added MIT license file

1.6.1
- Make search_mod only load launcher config if no --no-filter
- Use min() instead of inline if to pick smallest number between mod_list and search_limit
- Only make the 'Minecraft vanilla does not support mod' error shown when no --no-filter
- Remove intermediate response_json variable

1.6.2
- Add timeout to request functions
- check_eula_agreed now use .readlines instead of manually split in newlines
- Renamed slug_id to modid in add_mod
- Update the version search in add_mod
- Add error messages for mod version doesn\'t exists and no file marked as primary in add_mod
- Invert the if no no_filter condition
- Correct the condition in search_mod\'s skipped_message to be more than 0 instead of 1
- Simplified license name to use or instead inline if statement
- Add intermediate mod_license variable
- Replaced some bare Exception
- Update argparse help messages

1.6.3
- Fix bug when add_mod got 0 result from getting mod version
- Fix typo in request_get for timeout (tiemout)
- Add debug to output add_mod get version response
- "Downloading ..." message now includes filename

1.6.4
- Update User-Agent string
- Make the default action is print help and exit (./mcserver -> help)
- Extensively update argparse

1.6.5
- Get response_offset as reference
- Update skipped_message in search_mod to use response_offset instead of search_offset
- Add more info such as download and follows count when searching
- Change search_message to be 'Searching for mods with "<query>" in Modrinth...'

1.6.6
- Make isatty at the start of script instead of everytime color() got called
- Update *_config error messages
- Add "Got response status" in request_* debug message
- Add function fetch_mod_version for preparing to do BFS mod dependency resolution

1.6.7
- Print every dependency a mod need in add_command
- Renamed depended_mod to dependency in fetch_mod_version

1.6.8
- Add check if no primary file detected in fetch_mod_version
- "Fix" f-string, double quote inside double quote f-string

1.7.0
- Directly implement simple BFS mod dependency resolving for now, great -_-. not even iterating through couple of commits...
- Add check in wrap_text of int in *_indent where it supposed to be a str
- Renamed fetch_mod_version -> project_id to just id
- Removed "Got status code" debug messages

1.8.0
- Add SHA1 checksum inside request_download
- Add couple of flags in `init` to manipulate some configs
- Add vanilla server install

---

## 1.8.1
### Fixed
- Typo in mod dependency resolution

## 1.9.0
### Added
- Function to format large number with unit
### Changed
- Numbers now use the format number for easier reading
- `init` command options name changed

## 1.9.1
### Changed
- Update User-Agent to reflect username change
### Fixed
- A typo when --mc-version option is not used

## 1.9.2
### Changed
- Some command description and option description
- Size info include disclaimer of it also counts optional mods
- Moved debug environment and log level to the top
### Removed
- Moving tempfile to its destination debug log

## 1.9.3
### Changed
- Upgrade HTTP to HTTPS (Mojang APIs)

## 1.9.4
### Fixed
- Generating config now use deepcopy to avoid changing the default config

## 1.9.5
### Changed
- The script will exit with code 1 if any error happens

---

Following [Keep a changelog](https://keepachangelog.com/en/1.1.0/)

## [1.9.6] - 2026-03-16

### Added
- SHA512 option in `request_download`

### Changed
- Moved `colors` to "Variables" section
- Renamed `read_chunk_size` to `checksum_chunk_size`
- Renamed `initialize_directory` to `initialize_server` (and its error type)
- Rename `color_text` to `color_string`
- Update `format_number` error message
- Default timeout is now 10 (seconds)
- Replace \" to \' in `fetch_mod_version` error message
- Add "from Modrinth" in help message of command `show_mod`
- Update messages in `initialize_server` to reflect the function change
- Update some function calls to reflect those changes (rename function and added functionality)

### Fixed
- Check if dependency is already added as unresolved when initial fetching in `add_mod`

## [1.9.7] - 2026-03-16

### Added
- `show_mods` finally support multiple mods

### Changed
- Update `show_mods` output structure

## [1.9.8] - 2026-03-16

### Fixed
- Downloading mod uses the wrong dictionary for hashes, mod instead of mod_file

## [1.9.9] - 2026-03-16

### Added
- `--sort-by` option for `search_mod` used to specify what index to sort the mod
- `<modrinth>.sort_by` configuration, same as `--sort-by`

### Changed
- `format_number` behavior to include the last 2 decimal
- Not format numbering for mod counts and pages, instead now is just comma
- `add_mod` now more clarify that it will not download optional mods yet

## [1.9.10] - 2026-03-18

### Fixed
- Remove `format_number` for mod search result message in favor of more precise thousands separator instead

---

More correct semantic versioning:
1. MAJOR: When changes make older script configuration "broken"
2. MINOR: When add new thing for the user
3. PATCH: When changing how the script work

## [1.10.0] - 2026-03-18

### Added
- "manual" dependency type

### Changed
- Move the BFS dependency resolving to its own function (`resolve_mods_dependencies`)
- `fetch_mod_version` now use list of game version and loader instead of just 1 of them
- Type hinting for `resolve_mods_dependencies` and `fetch_mod_version`

### Fixed
- "embedded" is now not marked as resolved until a mod actually has different dependency type for it
- Adapted `manual` types to `required` for download mods logic (quick hack)

## [1.10.1] - 2026-03-19

### Added
- Type hinting to `fetch_url` and `download_url`

### Changed
- Renamed function `request_fetch` to `fetch_url`
- Renamed function `request_download` to `download_url`
- Hash are now calculated directly while downloading instead of separate read
- Renamed variable `checksum_chunk_size` to `read_chunk_size`
- Params `filename` in `download_url` is forced to be `Path` object

## [1.10.2] - 2026-03-19

### Added
- Add "Expected Hash" and "Got Hash" debug log

## [1.10.3] - 2026-03-19

### Added
- Add function `print_status`
- Add "Resolving mod..." dynamic message
- Add cursor-related ANSI code to `ansi_codes`

### Changed
- Renamed function `color` to `ansi`
- Renamed variable `colors` to `ansi_name`
- Renamed function `resolve_mods_dependencies` to `resolve_mods`
- Remove unnecesseary loop for `resolve_mods`
- `search_mod` now use color\_string

## [1.10.4] - 2026-03-19

### Fixed
- Removed duplicate "Client" in `search_mods`

## [1.10.5] - 2026-03-19

### Changed
- Edit message in `add_mods` from "Abort" to "Cancelled"

### [1.10.6] - 2026-03-20

### Changed
- Replace the hack of removing leading 0 of `format_number` using round(, 2) and :g

## [1.10.7] - 2026-03-21

### Changed
- Fix typo in `init_server` of configuration
- Removed leftover `number_format` variable

## [1.10.8] - 2026-03-21

### Fixed
- Remove "metavar" for "sort by" in `search_mod`

## [1.10.9] - 2026-03-21

### Added
- Log handler for clearing current line (adapting `print_status`)

### Changed
- Moved Modrinth API URL to a variable `modrinth_api`

### Fixed
- Corrected behavior of `print_status`

## [1.10.10] - 2026-03-22

### Changed
- `search_mod` now indent the initial with 2 spaces and subsequent by 1 space
- Use `enumerate` in `show_mods` as counter

## [1.10.11] - 2026-03-23

### Added
- Progress indicator for `download_url`

## [1.10.12] - 2026-03-23

### Added
- Option in `load_config` to `allow_missing`

### Changed
- Make `search` work without `init` (no "modrinth" or "server" config)

## [1.10.13] - 2026-03-24

### Added
- `plurarize` function

### Changed
- `search_mod` now use the `pluralize` function

## [1.10.14] - 2026-03-24

### Added
- `padding` parameter to `mod_environment_color`

### Changed
- Make the line in square brackets aligned to eachother in `search_mod`

## [1.10.15] - 2026-03-26

### Added
- Check if java in PATH

### Fixed
- Correct a simicolon to double colon

## [1.10.16] - 2026-03-26

### Added
- `resolved_mods`'s "dependency\_data" now return "manual" flag

### Changed
- Move progress bar from `add_mod` to `resolve_mods`
- `resolve_mod` now use deque instead of list for "unresolved\_mods"
- `fetch_mod_version` now uses `pluralize` in error message
- `fetch_mod_version` now raise a custom error message when mod doesn't exist

## [1.10.17] - 2026-03-26

### Added
- A dictionary for special plural
- "incompatible" mod list
- Colors in `add_mod`

### Changed
- Move `expected_hash` after the hash
- "total\_size" now only count required mods

## [1.10.18] - 2026-03-27

### Changed
- "incompatible\_mods" is now just in "resolved\mods\_data"

---

# Semantic Versioning (MAJOR.minor._patch_):
- MAJOR: When you introduce breaking changes (Rename a configuration file, rename directory, etc)
- minor: When you change user interaction (Add new command, add new flag to a command, etc)
- _patch_: When you change internal code without visible changes (Fix a typo, rework an algorithm, etc)

# Changelog Structure:
```md
## [<semver>] - <date(yyyy/MM/dd)>

### Added
- A

### Changed
- B

### Deprecating
- C

### Removed
- D

### Fixed
- E

### Security
- F```

## [1.11.0] - 2026-03-27

### Added
- `skip_embedded_dependencies` optional boolean parameter to `fetch_mod_version`
- `manual` key to each entry in `resolved_data`

### Changed
- Renamed `ResolveModsDependenciesError` to `ResolveModsError`
- Renamed `unresolved_mods` to `unresolved_entries`
- Renamed `resolved_mods` to `processed_ids`
- Renamed `resolved_mods_data` to `resolved_data`
- `resolve_mods` now use the `skip_embedded_dependencies`
- Reworked the dependency resolution logic to be "early-filtering"

## [1.11.1] - 2026-03-28

### Fixed
- Typo of `skip_embedded_dependecies` to `skip_embedded_dependencies`

## [1.11.2] - 2026-03-28

### Fixed
- Rename variable `resolved_dependencies` to `resolved_data` in `add_mod`

## [1.11.3] - 2026-03-28

### Added
- Added `dependants` in `resolved_data`

### Changed
- Completely reworked the `resolve_mods`, again...
- `resolve_mods` now return "dictionary" instead of "list" with the key being the mod id

## [1.11.4] - 2026-03-29

### Added
- Logic to migrate slug with existing ID entry

### Changed
- Mark "incompatible" dependency mods as processed to avoid fetching data for them

## [1.11.5] - 2026-03-30

### Added
- Error when trying to install two mods that has incompatible with one or another
- Enum-based mod dependency types
- String to list in `resolve_mods` and `fetch_mod_version`

### Changed
- Renamed `loaders` to `loaders_name` in `fetch_mod_version`
- Reworked the `resolve_mods`... again.

## [1.11.6] - 2026-03-30

### Changed
- The optional dependency version not found warning message now contains mod ID
- Make the mod dependency resolver only process required dependencies

### Fixed
- Download plural uses `follows` count instead of `downloads` count, now is fixed
- Replace `required` to `mod_dependency_types["required"]` in the download loop of `add_mod`

## [1.11.7] - 2026-03-30

### Fixed
- Typo in download loop of typing `mod_dependency_type` instead of `mod_dependency_types`, fixed
