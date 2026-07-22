# MCServer
## About
A CLI tool to manage Minecraft: Java Edition servers.

## Platform
Supported platforms:
- Linux
- and Termux.

## Requirements
- Python 3.14 or newer
- JRE (depends on Minecraft version)

## How to install
- System-wide (Requires root): 
1. Download the `mcserver` script file from GitHub releases
2. Move the file to `/usr/local/bin`
3. Run `chmod +x mcserver`

- Per-user:
1. Create a directory "bin"
2. Download the script from GitHub releases onto that directory
3. Give it "executable" permission with `chmod +x mcserver`
4. Add the directory in the PATH environment:
   - Run `export PATH=$HOME/bin:$PATH` if you're using shell that is POSIX-compliant like Bash, Zsh, or ash
   - Run `fish_add_path ~/bin` if you're using FISH

## Usage
- Add mods (and its dependencies): `mcserver add <mods>`
- Import a modpack: `mcserver import [file]`
- Initialize the server: `mcserver init [options]`
- Manage operator status: `mcserver op`
- Search mods from Modrinth: `mcserver search [<query>] [options]`
- Show mod information from Modrinth: `mcserver show <mods>`
- Start the server: `mcserver start`
- Stop the server: `mcserver stop`
- Manage the whitelist: `mcserver whitelist`

### Example
```bash
mcserver init --mc-version=1.20.1 --loader=fabric --loader-version=0.19.3
mcserver search --no-filter thdilos
mcserver show thdilos-fox-origin thdilos-fox-origin-expanded
mcserver add thdilos-fox-origin-expanded lithium tick-stasis ferrite-core krypton
mcserver start
```

## Note
This is a **Personal Project**, things may be unstable.