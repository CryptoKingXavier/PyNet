"""
Free Proxy List Automated Web Scraper
======================================

Website:
  https://free-proxy-list.net

Purpose:
  Automatically scrape the live proxy table exactly as rendered
  by a browser.

Features:
  - Uses Playwright browser automation
  - Handles JavaScript-rendered content
  - Extracts proxy details
  - Saves CSV and JSON output
  - Prints first 5 proxies
  - Includes error handling
  - Fully standalone script

Author:
  CryptoKingXavier

Requirements:
  pip install playwright pandas
  playwright install chromium

Run:
  python free_proxy_scraper.py
"""


# ============================
# IMPORTS
# ============================

import json
import pandas as pd
from os import getenv
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()

# ============================
# CONFIGURATION
# ============================

TARGET_URL = getenv("SITE")
OUTPUT_CSV = getenv("OUTPUT_CSV")
OUTPUT_JSON = getenv("OUTPUT_JSON")

# Maximum number of rows to scrape
# Set to None if you want every proxy
MAX_ROWS = None


# ============================
# SCRAPER FUNCTION
# ============================


def scrape_proxy_list():
  """
  Main scraping function.

  Returns:
    list[dict]:
      A list containing proxy information.
  """

  proxies = []

  # Start Playwright
  with sync_playwright() as playwright:
    # Launch Chromium browser
    #
    # headless=True:
    #   Runs invisibly in the background.
    #
    # Change to False if you want
    # to watch the browser scrape.
    browser = playwright.chromium.launch(headless=False)

    # Create browser context
    #
    # Adding a realistic user agent makes
    # the request behave closer to a normal browser.
    context = browser.new_context(
      user_agent=(
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138 Safari/537.36"
      )
    )

    # Open new page
    page = context.new_page()

    try:
      print("[INFO] Opening website...")

      page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)

      print("[INFO] Waiting for proxy table...")

      # Wait until the table rows exist.
      #
      # The site loads data dynamically,
      # so normal requests may not contain
      # the table.
      page.wait_for_selector("table tbody tr", timeout=60000)

      # Locate all table rows
      rows = page.locator("table tbody tr")

      total_rows = rows.count()

      print(f"[INFO] Found {total_rows} proxies")

      # Decide how many rows to scrape

      if MAX_ROWS:
        total_rows = min(total_rows, MAX_ROWS)

      # Loop through table rows

      for index in range(total_rows):
        columns = rows.nth(index).locator("td").all_inner_texts()

        # Expected columns:
        #
        # 0 IP Address
        # 1 Port
        # 2 Code
        # 3 Country
        # 4 Anonymity
        # 5 Google
        # 6 HTTPS
        # 7 Last Checked

        if len(columns) < 8:
          continue

        proxy = {
          "ip": columns[0].strip(),
          "port": columns[1].strip(),
          "code": columns[2].strip(),
          "country": columns[3].strip(),
          "anonymity": columns[4].strip(),
          "google": columns[5].strip(),
          "https": columns[6].strip(),
          "last_checked": columns[7].strip(),
          "scraped_at": (datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        }

        proxies.append(proxy)

    except PlaywrightTimeoutError:
      print("[ERROR] Timeout while loading table.")

    except Exception as error:
      print("[ERROR]", error)

    finally:
      # Always close browser
      browser.close()

  return proxies


# ============================
# SAVE FUNCTIONS
# ============================


def save_results(data):
  """
  Save scraped proxies into files.
  """

  if not data:
    print("[WARNING] No data found.")

    return

  # Convert to dataframe

  dataframe = pd.DataFrame(data)

  # Save CSV

  dataframe.to_csv(OUTPUT_CSV, index=False)

  # Save JSON

  with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

  print(f"[SUCCESS] Saved {len(data)} proxies")

  print(f"[FILE] {OUTPUT_CSV}")

  print(f"[FILE] {OUTPUT_JSON}")


# ============================
# MAIN PROGRAM
# ============================


if __name__ == "__main__":
  print(
    """
===================================
Free Proxy List Scraper
===================================
        """
  )

  proxy_data = scrape_proxy_list()

  # Display first result

  print("\nFIRST PROXY\n")

  for proxy in proxy_data[:1]:
    print(proxy)

  # Save everything

  save_results(proxy_data)

  print("\nDONE.")
