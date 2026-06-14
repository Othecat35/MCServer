# MCServer
## About
A CLI tool to manage a Minecraft: Java Edition server.

## Windows
This project is not designed for Windows, some behavior might be unexpected. Try use WSL instead.

## Termux
Yez I explicitly made it to works well in Termux, it is tge whole motivation to make it CLI only and avoiding dependency like requests (even though it worked on Termux)

## Requirements
- Python 3.12 or later
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
- Initialize the server: `mcserver init [options]`
- Install the server: `mcserver install`
- Search mods from Modrinth: `mcserver search [<query>] [options]`
- Show mods information from Modrinth: `mcserver show <mods>`
- Add mods (and its dependencies): `mcserver add <mods>`
- Start the server: `mcserver start`

## Note
This is a **personal project** for learning purpose, might be useful for myself.
