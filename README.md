# MCServer
## About
A Python script project that is created with sole purpose of helping with managing self-hosted Minecraft: Java Edition server (primarily, me).

## For Windows
I can't be sure if this script can work at all, but use WSL just in case. And no I don't even have hope with WSL either, so you're on your own.

## Requirements
- Python 3.12 or later
- JRE (depends on Minecraft version):
  - MC 1.0 - 1.16.5 : JRE 8
  - MC 1.17 - 1.17.1 : JRE 16
  - MC 1.18 - 1.20.4 : JRE 17
  - MC 1.20.5 - Later : JRE 21

## How to install
System-wide (Requires root): 
1. Download the `mcserver` script file
2. Move the file to `/usr/local/bin`
3. Run `chmod +x mcserver`

## Usage
Initialize directory: `mcserver init`
Start the server: `mcserver start`
Search mod from Modrinth: `mcserver search <query>`

## Note
This project is just a personal project, don't take this seriously! But, I do want to make this functional for those self-hoster nerds. Not tested at all, beware.
