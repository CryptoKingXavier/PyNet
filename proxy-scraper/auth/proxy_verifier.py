from os import getenv
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
  with open(getenv("IO_TXT"), "r") as f:
    proxies = f.read().split("\n")

  with open(getenv("VALID_PROXY_TXT"), "r") as f:
    valid_proxies = f.read().split("\n")

  proxy_maps: list[str] = list()

  for idx, valid_proxy in enumerate(valid_proxies, start=1):
    for _idx, proxy in enumerate(proxies, start=1):
      if valid_proxy == proxy:
        proxy_maps.append(
          f"[{idx}|{len(valid_proxies)}]-{valid_proxy} == [{_idx}|{len(proxies)}]-{proxy}"
        )

  with open(getenv("PROXY_MAP"), "w") as f:
    f.writelines(f"{proxy_map}\n" for proxy_map in proxy_maps)


if __name__ == "__main__":
  main()
