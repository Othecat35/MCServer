# MCServer
## About
A CLI tool to manage Minecraft: Java Edition servers.

## Platform
Supported platforms:
- Linux
- and Termux.

## Requirements
- Python 3.12 or newer (Python 3.14 is recommended)
- JRE (depends on Minecraft version)

## How to install
- Using pip: Just run `pip install mcserver-cli`

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
- Initialize a server: `mcserver init [options]`
- List operator players: `mcserver op list`
- Revoke operator players: `mcserver op revoke <players>`
- Search projects: `mcserver search [query] [options]`
- Show information about projects: `mcserver show <projects>`
- Start the server: `mcserver start`
- Stop the server: `mcserver stop`
- List whitelisted players: `mcserver whitelist list`
- Remove whitelisted players: `mcserver whitelist remove <players>`

### Examples
- Create and start a Fabric 1.20.1 server in the current directory
```bash
mcserver init --game-version=1.20.1 --loader=fabric
mcserver start
```

- Search top 50 Fabric mods for Minecraft 1.20.1 on modrinth
```bash
mcserver search --loader=fabric --game-version=1.20.1 --limit=50
```

- List all operator and whitelisted players on current directory
```bash
mcserver op list
mcserver whitelist list
```

- Adding a player to the whitelist
```bash
mcserver whitelist add Notch
```

- Granting Notch operator level 4 and can bypass player limit
```bash
mcserver op grant Notch --permission-level=4 --bypasses-player-limit
```

- Remove me from the whitelist
```bash
mcserver whitelist remove Othecat35
```

- Stop a running server on current directory with sigterm
```bash
mcserver stop
```

## Note
This is a **Personal Project** by Othecat35, so don't expect much from me :>
