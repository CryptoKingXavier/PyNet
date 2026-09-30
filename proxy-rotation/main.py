from requests import get

with open("./valid_proxies.txt", "r") as f:
  proxies = f.read().split("\n")

sites_to_check = [
  "http://books.toscrape.com/",
  "http://books.toscrape.com/catalogue/category/books/fantasy_19/index.html",
  "http://books.toscrape.com/catalogue/category/books/history_32/index.html",
]

counter = 0

for site in sites_to_check:
  try:
    print(f"Using the proxy: {proxies[counter]}")
    res = get(site, proxies={"http": proxies[counter], "https": proxies[counter]})
    print(f"Status code for {site}: {res.status_code}")
  except Exception as e:
    print(f"Error accessing {site} with proxy {proxies[counter]}: {e}")
  finally:
    counter += 1
    if counter >= len(proxies):
      counter = 0
