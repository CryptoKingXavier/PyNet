"""
Wi-Fi Network Scanner
Scan nearby Wi-Fi networks and view SSID, signal, channel, and security
"""

# import required libraries
from os import name, system
from subprocess import check_output


def main() -> None:
  # run windows command to get available networks
  command: str = "netsh wlan show networks mode=bssid"
  output = check_output(command, shell=True)
  decoded = output.decode(errors="ignore")

  # parse and display the results
  networks, current = list(), dict()

  for line in decoded.splitlines():
    line = line.strip()

    if line.startswith("SSID "):
      if current:
        networks.append(current)
        current = dict()
      current["ssid"] = line.split(":", 1)[1].strip()
    elif "Signal" in line:
      current["signal"] = line.split(":", 1)[1].strip()
    elif "Channel" in line:
      current["channel"] = line.split(":", 1)[1].strip()
    elif "Authentication" in line:
      current["security"] = line.split(":", 1)[1].strip()

  if current:
    networks.append(current)

  print("\n[*] Nearby Wi-Fi Networks:\n")
  for idx, network in enumerate(networks, start=1):
    print(
      f"[{idx}] {network.get('ssid', 'N/A')} | "
      f"Signal: {network.get('signal', 'N/A')} | "
      f"Security: {network.get('security', 'N/A')} | "
      f"Channel: {network.get('channel', 'N/A')}"
    )


if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
