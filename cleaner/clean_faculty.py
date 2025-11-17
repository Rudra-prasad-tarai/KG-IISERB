#!/usr/bin/env python3
"""
clean_faculty.py

Usage:
    python3 clean_faculty.py --input_html faculty.html --output_dir ./cleaned_html

Outputs a clean, human-readable text file with the SAME NAME as input:

 faculty.html → cleaned_html/faculty.txt
"""

import os
import argparse
import re
from bs4 import BeautifulSoup, Comment


# -----------------------------------------------------------
# Normalize helper
# -----------------------------------------------------------
def norm(text):
    if not text:
        return ""
    return " ".join(text.split()).strip()


# -----------------------------------------------------------
# Phone regex (matches all formats)
# -----------------------------------------------------------
PHONE_REGEX = re.compile(
    r"(\+91[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4})"
)


# -----------------------------------------------------------
# Parse a faculty block
# -----------------------------------------------------------
def parse_faculty_block(block):
    text = block.get_text(" ", strip=True)
    if not text:
        return None

    name = None
    homepage = None
    emails = []
    phone = None
    role = None
    research = []

    # NAME
    for tag in ["h6", "h5", "h4", "h3"]:
        t = block.find(tag)
        if t:
            name = norm(t.get_text())
            break

    if not name:
        for c in block.find_all(["span", "a"]):
            t = c.get_text(strip=True)
            if any(x in t.lower() for x in ["prof", "dr", "mr", "ms"]):
                if len(t.split()) <= 6:
                    name = t
                    break

    # HOMEPAGE
    for a in block.find_all("a"):
        href = a.get("href", "")
        if href.startswith("http"):
            homepage = href

    # EMAIL
    parts = text.replace(":", " ").split()
    for p in parts:
        if "@iiserb.ac.in" in p or "[at]iiserb.ac.in" in p:
            cleaned = (
                p.replace("[at]", "@")
                 .replace("[At]", "@")
                 .replace("[AT]", "@")
                 .replace("(at)", "@")
                 .replace("at]", "@")
            )
            emails.append(cleaned)

    # PHONE (regex)
    m = PHONE_REGEX.search(text)
    if m:
        phone = m.group(1)

    # ROLE
    for rk in ["Assistant Professor", "Associate Professor", "Professor", "Dept. Head"]:
        if rk.lower() in text.lower():
            role = rk
            break

    # RESEARCH AREAS
    if "Research" in text:
        r = text.split("Research", 1)[1]
        r = r.replace(":", "")
        fields = [
            norm(x)
            for x in re.split(r"[;,]", r)
            if norm(x)
        ]
        research.extend(fields)

    if not name and not emails:
        return None

    return {
        "name": name or "",
        "role": role or "",
        "emails": emails,
        "phone": phone or "",
        "research": research,
        "homepage": homepage or "",
    }


# -----------------------------------------------------------
# Extract all faculty entries from HTML
# -----------------------------------------------------------
def extract_faculty_entries(soup):
    faculty = []

    # IISER style <article>
    for art in soup.find_all("article"):
        entry = parse_faculty_block(art)
        if entry:
            faculty.append(entry)

    # Google Sites style blocks
    for blk in soup.find_all("div", class_="tyJCtd"):
        entry = parse_faculty_block(blk)
        if entry:
            faculty.append(entry)

    # Backup: any block containing "Email"
    for eb in soup.find_all(string=lambda x: isinstance(x, str) and "Email" in x):
        parent = eb.find_parent()
        if parent:
            entry = parse_faculty_block(parent)
            if entry:
                faculty.append(entry)

    # Deduplicate
    final = []
    seen = set()
    for f in faculty:
        name = f.get("name", "")
        if name and name not in seen:
            final.append(f)
            seen.add(name)

    return final


# -----------------------------------------------------------
# Format output
# -----------------------------------------------------------
def format_faculty_list(flist):
    lines = []
    for f in flist:
        lines.append("----------------------------------------")
        lines.append(f"Name: {f['name']}")
        if f["role"]:
            lines.append(f"Role: {f['role']}")
        if f["emails"]:
            lines.append("Email(s): " + ", ".join(f["emails"]))
        if f["phone"]:
            lines.append(f"Phone: {f['phone']}")
        if f["research"]:
            lines.append("Research Areas:")
            for r in f["research"]:
                lines.append(f" - {r}")
        if f["homepage"]:
            lines.append(f"Homepage: {f['homepage']}")
        lines.append("----------------------------------------\n")
    return "\n".join(lines)


# -----------------------------------------------------------
# Clean a single file
# -----------------------------------------------------------
def clean_html_file(infile, outfile):
    with open(infile, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # remove noise
    for tag in soup(["script", "style"]):
        tag.decompose()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()

    faculty = extract_faculty_entries(soup)
    cleaned = format_faculty_list(faculty)

    with open(outfile, "w", encoding="utf-8") as f:
        f.write(cleaned)


# -----------------------------------------------------------
# CLI
# -----------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_html", required=True, help="A single faculty HTML file")
    parser.add_argument("--output_dir", default="cleaned_html")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    infile = args.input_html
    if not infile.lower().endswith(".html"):
        print("[-] Error: input must be .html")
        return

    # SAME OUTPUT NAME, but .txt
    base = os.path.basename(infile)
    outname = base.replace(".html", ".txt")
    outfile = os.path.join(args.output_dir, outname)

    print(f"[+] Cleaning: {infile}")
    clean_html_file(infile, outfile)
    print(f"[✓] Saved cleaned output to: {outfile}")


if __name__ == "__main__":
    main()
