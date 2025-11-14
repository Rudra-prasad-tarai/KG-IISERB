#!/usr/bin/env python3

import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT_DIR = "html_dumps"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def save_html(url, name):
    print(f"\nFetching: {url}")
    driver = get_driver()
    driver.get(url)

    time.sleep(4)  # wait for JS to load

    html = driver.page_source
    driver.quit()

    out_path = f"{OUTPUT_DIR}/{name}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Saved {out_path}")


if __name__ == "__main__":
    save_html("https://dse.iiserb.ac.in/people.php", "faculty_page")
    save_html("https://dse.iiserb.ac.in/postdoc.php", "postdocs_page")

    save_html("https://dsestudents.iiserb.ac.in/phd", "phd_students_page")
    save_html("https://dsestudents.iiserb.ac.in/bs-ms-5th-year", "ms_5th_year_page")
    save_html("https://dsestudents.iiserb.ac.in/bs-ms-majors-4th-year", "bsms_4th_year_page")
    save_html("https://dsestudents.iiserb.ac.in/bs-ms-majors-3rd-year", "bsms_3rd_year_page")
