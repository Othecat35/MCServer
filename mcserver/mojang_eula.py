#Modules
# Standard
import time

from pathlib import Path

#Paths
eula_file = Path("eula.txt")

#Functions
def is_eula_agreed() -> bool:
  try:
    for line in eula_file.read_text().split("\n"):
      if line.startswith("eula=true"):
        return True
  except FileNotFoundError:
    pass

  return False

def eula_agree() -> None:
  timestamp = time.strftime("%a %b %d %H:%M:%S GMT %Y", time.gmtime())
  eula_file.write_text(f"""#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).
#{timestamp}
eula=true""")
