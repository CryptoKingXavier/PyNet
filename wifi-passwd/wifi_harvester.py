# Pythonic Wi-Fi Key Harvester
from os import name, system
from re import findall, search
from subprocess import check_output, DEVNULL

def get_wifi_passwords():
  print("--- Scanning Saved WiFi Networks ---")

  try:
    # 1. Get all profile names
    raw_output = check_output(
      "netsh wlan show profiles",
      shell=True,
      stderr=DEVNULL
    ).decode("utf-8", errors="ignore")

    # Regex to capture profile names across different Windows language variations
    ssids = findall(r"(?:All User Profile\s*:\s*)(.*)", raw_output)

    if not ssids:
      print("No saved WiFi profiles found."); return

    # 2. Display networks to user
    for i, ssid in enumerate(ssids, 1): print(f"[{i}] {ssid.strip()}")

    # 3. Get user choice
    while True:
      try:
        choice = int(input(f"\nSelect network index (1-{len(ssids)}) to view password: "))
        if 1 <= choice <= len(ssids):
          target_ssid = ssids[choice - 1].strip(); break
        print("Invalid index. Please select a number from the list.")
      except ValueError: print("Please enter a valid number.")

    print(f"\n--- Retrieving Key for: '{target_ssid}' ---")

    # 4. Extract password for chosen network
    profile_output = check_output(
      f'netsh wlan show profile name="{target_ssid}" key=clear',
      shell=True,
      stderr=DEVNULL
    ).decode("utf-8", errors="ignore")

    password_match = search(r"(?:Key Content\s*:\s*)(.*)", profile_output)

    # 5. Output results
    print(f"Network: {target_ssid}")

    if password_match: print(f"Password: {password_match.group(1).strip()}")
    else: print("Password: None (Open Network or Security Key Hidden)")

  except Exception as e: print(f"An error occurred: {e}")

if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  get_wifi_passwords()
