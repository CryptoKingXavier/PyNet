from os import getenv
from queue import Queue
from requests import get
from http import HTTPStatus
from threading import Thread
from dotenv import load_dotenv

load_dotenv()


def check_proxies() -> None:
  q: Queue = Queue()
  valid_proxies = list()

  with open(getenv("IO_TXT"), "r") as f:
    proxies = f.read().split("\n")
    for proxy in proxies:
      q.put(proxy)

  while not q.empty():
    proxy = q.get()

    try:
      res = get(getenv("PROXY_SITE"), proxies={"http": proxy, "https": proxy})
    except Exception:
      continue

    if res.status_code == HTTPStatus.OK.value:
      print(f"Valid proxy: {proxy}")
      valid_proxies.append(proxy)

  with open(getenv("VALID_PROXY_TXT"), "w") as f:
    f.writelines(f"{valid_proxy}\n" for valid_proxy in valid_proxies)


def main() -> None:
  for _ in range(int(getenv("THREADS"))):
    Thread(target=check_proxies).start()


if __name__ == "__main__":
  main()
