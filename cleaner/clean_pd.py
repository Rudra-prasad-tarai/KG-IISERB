#!/usr/bin/env python3
"""
clean_postdoc.py

Cleaner for Post-Doctoral section HTML pages.

Extracts:
 - Name
 - Year of Joining
 - Supervisor Name
 - Email (handles [At] → @)
 - Homepage/Weblink
 - Image URL

Usage:
    python3 clean_postdoc.py --input postdoc.html --output_dir ./cleaned_postdoc
"""

import os
import argparse
from bs4 import BeautifulSoup


def norm(s):
    if not s:
        return ""
    return " ".join(s.split()).strip()


def parse_postdoc_entry(article):
    """
    Parse one <article class="one_third"> block
    containing one post-doctoral entry.
    """

    entry = {
        "name": "",
        "year_of_joining": "",
        "supervisor": "",
        "email": "",
        "homepage": "",
        "image_url": "",
    }

    # -----------------------------
    # IMAGE
    # -----------------------------
    img_tag = article.find("img")
    if img_tag and img_tag.get("src"):
        entry["image_url"] = img_tag["src"]

    # -----------------------------
    # NAME
    # -----------------------------
    name_tag = article.find("h6", class_="heading")
    if name_tag:
        entry["name"] = norm(name_tag.get_text(" ", strip=True))

    # -----------------------------
    # DETAILS inside <p>
    # -----------------------------
    p = article.find("p")
    if p:
        text = p.get_text(" ", strip=True)

        # Year of Joining
        if "Year of Joining" in text:
            y = text.split("Year of Joining:")[1].split("Supervisor")[0]
            entry["year_of_joining"] = norm(y)

        # Supervisor
        if "Supervisor Name" in text:
            s = text.split("Supervisor Name:")[1].split("Email")[0]
            entry["supervisor"] = norm(s)

        # Email
        if "Email" in text:
            e = text.split("Email:")[1].split()[0]
            e = e.replace("[At]", "@").replace("[at]", "@")
            entry["email"] = e

        # Homepage (weblink)
        link = p.find("a")
        if link and link.get("href"):
            entry["homepage"] = link.get("href")

    # Validate
    if not entry["name"]:
        return None

    return entry


def clean_file(input_html, output_txt):
    with open(input_html, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    articles = soup.find_all("article", class_="one_third")

    entries = []
    for art in articles:
        e = parse_postdoc_entry(art)
        if e:
            entries.append(e)

    # Write clean output
    with open(output_txt, "w", encoding="utf-8") as f:
        for e in entries:
            f.write("----------------------------------------\n")
            f.write(f"Name: {e['name']}\n")
            if e['year_of_joining']:
                f.write(f"Year of Joining: {e['year_of_joining']}\n")
            if e['supervisor']:
                f.write(f"Supervisor: {e['supervisor']}\n")
            if e['email']:
                f.write(f"Email: {e['email']}\n")
            if e['homepage']:
                f.write(f"Homepage: {e['homepage']}\n")
            if e['image_url']:
                f.write(f"Image: {e['image_url']}\n")
            f.write("----------------------------------------\n\n")

    print(f"[✓] Cleaned postdoc data saved → {output_txt}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to postdoc HTML file")
    parser.add_argument("--output_dir", default="./cleaned_postdoc", help="Directory to save cleaned file")
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output_dir

    # Create directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Output filename based on input
    base = os.path.basename(input_file).rsplit(".", 1)[0]
    output_file = os.path.join(output_dir, base + "_clean.txt")

    clean_file(input_file, output_file)


if __name__ == "__main__":
    main()
