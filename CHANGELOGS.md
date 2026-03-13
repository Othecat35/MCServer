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
- Move java command options to a seperate launcher.json configuration

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
- Added option '--no-filter' to 'search' mod without version-dependant filter

1.5.1
- Added failback value for mod_environment_color()
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
- Replaced some bare Excetion
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

### Romoved
- Moving tempfile to its destination debug log