from queue import Queue
from requests import get
from threading import Thread

q: Queue = Queue()
valid_proxies = list()

with open("./proxy_list.txt", "r") as f:
  proxies = f.read().split("\n")
  for proxy in proxies:
    q.put(proxy)


def check_proxies():
  global q
  while not q.empty():
    proxy = q.get()

    try:
      res = get("http://ipinfo.io/json", proxies={"http": proxy, "https": proxy})
    except Exception:
      continue

    if res.status_code == 200:
      print(f"Valid proxy: {proxy}")
      valid_proxies.append(proxy)

  with open("./valid_proxies.txt", "w") as f:
    f.writelines(f"{valid_proxy}\n" for valid_proxy in valid_proxies)


def main():
  for _ in range(10):
    Thread(target=check_proxies).start()


if __name__ == "__main__":
  main()
