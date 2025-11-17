#!/usr/bin/env python3
"""
clean_phd.py

Cleaner for PhD Students section from a Google Sites HTML file.

Extracts:
 - Name
 - Year of Joining
 - Supervisor
 - Email (handles missing mailto)
 - Homepage
 - Image URL

Usage:
    python3 clean_phd.py --input phds.html --output_dir ./cleaned_phd
"""

import os
import argparse
from bs4 import BeautifulSoup


def norm(s):
    if not s:
        return ""
    return " ".join(s.split()).strip()


def parse_student_block(block):
    """
    Given a <div class="tyJCtd ..."> block for a single PhD student,
    extract relevant information.
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
    # 1. NAME + HOMEPAGE
    # -----------------------------
    name_link = block.find("a")
    if name_link:
        entry["name"] = norm(name_link.get_text(" ", strip=True))
        href = name_link.get("href", "")
        if href.startswith("http"):
            entry["homepage"] = href

    # -----------------------------
    # 2. IMAGE URL
    # -----------------------------
    img = block.find("img")
    if img and img.get("src"):
        entry["image_url"] = img["src"]

    # -----------------------------
    # 3. PARSE PARAGRAPHS (<p> tags)
    # -----------------------------
    for p in block.find_all("p"):
        txt = norm(p.get_text(" ", strip=True))

        # Year of joining
        if "Year of Joining" in txt:
            parts = txt.split(":")
            if len(parts) > 1:
                entry["year_of_joining"] = norm(parts[1])

        # Supervisor
        if "Supervisor" in txt:
            clean = txt.replace("Supervisor", "").replace(":", "").strip()
            entry["supervisor"] = norm(clean)

        # Email (robust handling)
        if "Email" in txt:
            mail = p.find("a")
            if mail:
                href = mail.get("href", "").strip()

                # Case 1: Proper mailto link
                if href.startswith("mailto:"):
                    e = href.replace("mailto:", "").replace("[at]", "@")
                    entry["email"] = e

                # Case 2: href="" but email text is inside
                else:
                    inner = mail.get_text(" ", strip=True)
                    inner = inner.replace("[at]", "@")
                    if "@" in inner:  # simple validation
                        entry["email"] = inner

    # Reject blocks missing names → they are not student entries
    if not entry["name"]:
        return None

    return entry


def clean_file(input_html, output_txt):
    with open(input_html, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Google Sites puts each student inside: <div class="tyJCtd">
    blocks = soup.find_all("div", class_="tyJCtd")

    students = []
    for blk in blocks:
        student = parse_student_block(blk)
        if student:
            students.append(student)

    # Write clean, structured output
    with open(output_txt, "w", encoding="utf-8") as f:
        for s in students:
            f.write("----------------------------------------\n")
            f.write(f"Name: {s['name']}\n")
            if s['year_of_joining']:
                f.write(f"Year of Joining: {s['year_of_joining']}\n")
            if s['supervisor']:
                f.write(f"Supervisor: {s['supervisor']}\n")
            if s['email']:
                f.write(f"Email: {s['email']}\n")
            if s['homepage']:
                f.write(f"Homepage: {s['homepage']}\n")
            if s['image_url']:
                f.write(f"Image: {s['image_url']}\n")
            f.write("----------------------------------------\n\n")

    print(f"[✓] Cleaned PhD data saved → {output_txt}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to the PhD HTML file")
    parser.add_argument("--output_dir", default="./cleaned_phd", help="Directory to save cleaned output")
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output_dir

    # Create output directory if missing
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename based on input file
    base = os.path.basename(input_file).rsplit(".", 1)[0]
    output_file = os.path.join(output_dir, base + "_clean.txt")

    clean_file(input_file, output_file)


if __name__ == "__main__":
    main()
