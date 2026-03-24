# MCServer
## About
A Python script CLI tool that is created for helping with managing self-hosted Minecraft: Java Edition server with Modrinth intergration.

## Windows
I'm not sure if this script would work in Windows, because of my environment is just Linux. But as an alternative, try using WSL.

## Requirements
- Python 3.12 or later
- JRE (depends on Minecraft version): (currently not supporting multiple JRE selection nor check if they even exists or work with the server version)
  - MC 1.0 - 1.16.5 : JRE 8
  - MC 1.17 - 1.17.1 : JRE 16
  - MC 1.18 - 1.20.4 : JRE 17
  - MC 1.20.5 - Later : JRE 21

## How to install
- System-wide (Requires root): 
1. Download the `mcserver` script file
2. Move the file to `/usr/local/bin`
3. Run `chmod +x mcserver`

- Per-user:
1. Create a directory "bin"
2. Download the script onto that directory
3. Give it "executable" permission with `chmod +x mcserver`
4. Add the directory in the PATH environment:
   - Run `export PATH=$HOME/bin:$PATH` if you're using shell that is POSIX-compliant like Bash, Zsh, or ash
   - Run `fish_add_path ~/bin` if you're using FISH

## Usage
- Initialize the server: `mcserver init [options]`
- Install the server: `mcserver install`
- Search mods from Modrinth: `mcserver search [<query>] [options]`
- Show mods information from Modrinth: `mcserver show <mods>`
- Start the server: `mcserver start`

## Note
This project is just a personal project, don't take this seriously! But, I do want to make this much functional for those self-hoster nerds.
