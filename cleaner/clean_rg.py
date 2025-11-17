#!/usr/bin/env python3
"""
clean_research.py

Clean and extract structured information from research group HTML pages.

Supported patterns:
 - Image-left / text-right
 - Text-left / image-right
 - Multi-paragraph descriptions
 - Description split across multiple <p> and raw text nodes
 - <br>, empty <p>, and broken-line cleanup
 - Variations in homepage link wording (HomePage, Group Link, etc.)

Extracts:
 - Research Group Title
 - Image URL
 - Full cleaned description
 - Research Topics (UL > LI)
 - Homepage URL

Usage:
    python3 clean_research.py --input research.html --output_dir ./cleaned_research
"""

import os
import argparse
from bs4 import BeautifulSoup, NavigableString


def norm(s):
    if not s:
        return ""
    return " ".join(s.split())


def extract_description(text_block):
    """
    Extract clean description from:
    - <p>
    - broken lines
    - raw text nodes
    """

    desc_lines = []

    # Gather all <p> in order
    for p in text_block.find_all("p", recursive=False):
        txt = p.get_text(" ", strip=True)
        if txt:
            desc_lines.append(txt)

    # Also gather raw text nodes outside <p> but inside main block
    for node in text_block.children:
        if isinstance(node, NavigableString):
            t = norm(str(node))
            if t:
                desc_lines.append(t)

    # Join all collected description parts
    final_desc = " ".join(desc_lines)
    return norm(final_desc)


def parse_research_container(container):
    """
    Parse one <div class="research-container"> block.
    Handles swapped left-right layouts & broken HTML.
    """

    entry = {
        "title": "",
        "description": "",
        "topics": [],
        "homepage": "",
        "image_url": ""
    }

    halves = container.find_all("div", class_="one_half")
    if not halves:
        return None

    # Identify image block & text block
    img_block = None
    text_block = None

    for h in halves:
        img = h.find("img")
        if img and img.get("src"):
            img_block = h
        else:
            text_block = h

    # Fallback: first half always image if it includes <img>
    if not img_block and halves:
        for h in halves:
            if h.find("img"):
                img_block = h

    # -----------------------------
    # IMAGE
    # -----------------------------
    if img_block:
        img_tag = img_block.find("img")
        if img_tag and img_tag.get("src"):
            entry["image_url"] = img_tag["src"]

    # -----------------------------
    # TEXT CONTENT
    # -----------------------------
    if not text_block:
        return None

    # TITLE
    h3 = text_block.find("h3")
    if h3:
        entry["title"] = norm(h3.get_text(" ", strip=True))

    # DESCRIPTION
    entry["description"] = extract_description(text_block)

    # TOPICS
    ul = text_block.find("ul")
    if ul:
        for li in ul.find_all("li"):
            t = norm(li.get_text(" ", strip=True))
            if t:
                entry["topics"].append(t)

    # HOMEPAGE
    link = text_block.find("a")
    if link and link.get("href"):
        entry["homepage"] = link["href"]

    # If nothing valid extracted, skip
    if not entry["title"]:
        return None

    return entry


def clean_file(input_html, output_txt):
    with open(input_html, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    containers = soup.find_all("div", class_="research-container")
    entries = []

    for c in containers:
        e = parse_research_container(c)
        if e:
            entries.append(e)

    with open(output_txt, "w", encoding="utf-8") as f:
        for e in entries:
            f.write("----------------------------------------\n")
            f.write(f"Research Group: {e['title']}\n")

            if e["image_url"]:
                f.write(f"Image: {e['image_url']}\n\n")

            if e["description"]:
                f.write("Description:\n")
                f.write(e["description"] + "\n\n")

            if e["topics"]:
                f.write("Research Topics:\n")
                for t in e["topics"]:
                    f.write(f" - {t}\n")
                f.write("\n")

            if e["homepage"]:
                f.write(f"Homepage: {e['homepage']}\n")

            f.write("----------------------------------------\n\n")

    print(f"[✓] Cleaned research data saved → {output_txt}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to research HTML file")
    parser.add_argument("--output_dir", default="./cleaned_research",
                        help="Directory to save cleaned file")
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    base = os.path.basename(input_file).rsplit(".", 1)[0]
    output_file = os.path.join(output_dir, base + "_clean.txt")

    clean_file(input_file, output_file)


if __name__ == "__main__":
    main()
