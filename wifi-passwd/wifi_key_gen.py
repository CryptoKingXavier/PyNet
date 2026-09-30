from re import search
from os import name, system
from subprocess import check_output, DEVNULL

def main() -> None:
  commands: dict[str, str] = {
    "profiles": r'netsh wlan show profiles',
    "profile": r'netsh wlan show profile "wifi" key=clear',
  }

  profiles = check_output(
    commands.get("profiles"),
    shell=True,
    stderr=DEVNULL
  ).decode("utf-8", errors="ignore")

  names: list[str] = [
    line.split(":")[1].strip() \
    for line in profiles.split("\n") \
    if "All User Profile" in line
  ]

  for (i, n) in enumerate(names, start=1):
    print(f"{i} {n}")

  wifi_idx: int = int(input("\nChoose Wi-Fi Number: "))

  wifi = names[wifi_idx - 1]

  result = check_output(
    commands.get("profile").replace("wifi", wifi),
    shell=True,
    stderr=DEVNULL
  ).decode("utf-8", errors="ignore")

  password_match = search(r"(?:Key Content\s*:\s*)(.*)", result)

  # 5. Output results
  print(f"Network: {wifi}")

  if password_match: print(f"Password: {password_match.group(1).strip()}")
  else: print("Password: None (Open Network or Security Key Hidden)")

if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
