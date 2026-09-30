from httpx import Client
from pathlib import Path
from typing import Union
from pprint import pprint
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv, name, system

load_dotenv()


def init() -> None:
  for path in [
    "IO_HTML",
    "OUTPUT_CSV",
    "OUTPUT_JSON",
    "IO_TXT",
    "PROXY_MAP",
    "VALID_PROXY_TXT",
  ]:
    Path(getenv(path)).write_text("")
    system(f"curl -o {getenv('IO_HTML')} {getenv('SITE')}")


def extract_table() -> Union[dict[str, str], list[str]]:
  with open(getenv("IO_HTML"), "r", encoding="utf-8") as html_file:
    soup = BeautifulSoup(html_file, "lxml")

  proxy_map = [
    dict(
      zip(
        [th.text for th in soup.table.thead.find_all("th")],
        [td.text for td in row.find_all("td")],
      )
    )
    for row in soup.table.tbody.find_all("tr")
  ]

  proxies = [proxy.get("IP Address") for proxy in proxy_map]

  return proxies


def extract_textarea() -> list[str]:
  with open(getenv("IO_HTML"), "r", encoding="utf-8") as html_file:
    soup = BeautifulSoup(html_file, "lxml")

  proxies = soup.textarea.text.split("\n")[4:-1]

  return proxies


def main() -> None:
  init()

  # Choose extraction method: table/textarea
  proxies = extract_textarea()

  with open(getenv("IO_TXT"), "w", encoding="utf-8") as f:
    f.writelines(f"{proxy}\n" for proxy in proxies)

  print(f"DONE! {len(proxies)} Proxies Saved!")

  from auth.check_proxies import main as check_proxies_main

  check_proxies_main()

  from auth.proxy_verifier import main as proxy_verifier_main

  proxy_verifier_main()


if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
