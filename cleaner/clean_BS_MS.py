#!/usr/bin/env python3
"""
clean.py

Usage:
    python3 clean.py --input ./html_dumps/faculty.html
    python3 clean.py --input ./html_dumps/faculty.html --output_dir ./cleaned_html

Features:
 - Extracts visible text from HTML (Google Sites, IISER pages, etc.)
 - Extracts REAL tables
 - Extracts ESCAPED embedded tables (Google Sites <iframe>/data-code style)
 - Extracts ALL <a> links in "text | url" format
 - Repairs malformed table rows (Google Sites merges rows together)
 - Ensures each record stays on its own line
 - Writes a single cleaned .txt file for the provided HTML input
"""

import os
import argparse
import html as html_module
from bs4 import BeautifulSoup, Comment
from bs4 import NavigableString

# ---------------------------------------------------------
# CELL + TABLE PARSING
# ---------------------------------------------------------

def extract_clean_cell(cell):
    """
    Extract text + links from a table cell.
    Output example:
        'GitHub/LinkedIn ; GitHub/LinkedIn | https://github.com/XYZ'
    """
    parts = []

    # normal text
    text = " ".join(cell.stripped_strings)
    text = " ".join(text.split())
    if text:
        parts.append(text)

    # links (Option C)
    for a in cell.find_all("a"):
        link_text = " ".join(a.stripped_strings)
        link_url = a.get("href", "").strip()
        if link_text or link_url:
            parts.append(f"{link_text} | {link_url}")

    return " ; ".join(parts).strip()


def table_to_text(table_soup):
    """
    Convert a <table> into a clean multi-line text block.
    Fixes malformed rows from Google Sites by splitting every N cells (heuristic).
    """
    lines = []
    rows = table_soup.find_all("tr")

    for row in rows:
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        cleaned_cells = [extract_clean_cell(c) for c in cells]

        # Heuristic: if a row contains many cells (merged), split into chunks.
        # Default chunk_size can be tuned; 5 is a reasonable default for many site tables.
        chunk_size = 5
        if len(cleaned_cells) > chunk_size:
            for i in range(0, len(cleaned_cells), chunk_size):
                subrow = cleaned_cells[i:i+chunk_size]
                if subrow:
                    lines.append(" | ".join(subrow))
        else:
            lines.append(" | ".join(cleaned_cells))

    return "\n".join(lines)


def extract_real_tables(soup):
    """
    Extract proper <table> tags.
    """
    results = []
    for t in soup.find_all("table"):
        txt = table_to_text(t)
        if txt:
            results.append(txt)
    return results


def extract_escaped_tables(soup):
    """
    Handles cases where tables are embedded as escaped HTML:
        data-code="&lt;table&gt;..."
    or raw text containing escaped <table>.
    """
    found = []
    ATTR_FIELDS = ["data-code", "data-html", "data-content", "data-src", "data-url", "aria-label"]

    # Inspect attributes
    for tag in soup.find_all(True):
        for attr in ATTR_FIELDS:
            if tag.has_attr(attr):
                val = tag.get(attr)
                if val and ("<table" in val or "&lt;table" in val):
                    try:
                        unescaped = html_module.unescape(val)
                        inner = BeautifulSoup(unescaped, "html.parser")
                        for t in inner.find_all("table"):
                            txt = table_to_text(t)
                            if txt:
                                found.append(txt)
                    except Exception:
                        pass

    # Inspect raw text
    candidates = soup.find_all(
        string=lambda s: isinstance(s, str) and ("<table" in s or "&lt;table" in s)
    )

    for s in candidates:
        try:
            unescaped = html_module.unescape(s)
            inner = BeautifulSoup(unescaped, "html.parser")
            for t in inner.find_all("table"):
                txt = table_to_text(t)
                if txt:
                    found.append(txt)
        except Exception:
            pass

    # Deduplicate while preserving order
    final_list = []
    for f in found:
        if f not in final_list:
            final_list.append(f)

    return final_list


# ---------------------------------------------------------
# VISIBLE TEXT EXTRACTION
# ---------------------------------------------------------

def extract_visible_text(soup):
    """
    Extract readable text + links (text | url) outside tables.
    Add newlines at major boundaries (sections/headings).
    """
    TEXT_TAGS = [
        "p", "span", "div", "section", "li",
        "h1", "h2", "h3", "h4", "h5", "h6"
    ]

    out = []

    for tag in soup.find_all(TEXT_TAGS):
        if tag.find_parent(["script", "style"]):
            continue

        # Combine visible strings for this tag
        txt = " ".join([s for s in tag.stripped_strings if not isinstance(s, Comment)])
        txt = " ".join(txt.split())
        if txt:
            out.append(txt)

        # Append links found inside this tag in "text | url" form
        for a in tag.find_all("a"):
            link_text = " ".join(a.stripped_strings)
            link_url = a.get("href", "").strip()
            if link_text or link_url:
                out.append(f"{link_text} | {link_url}")

        # Add blank line after big structural tags to indicate section break
        if tag.name in ["section", "h1", "h2", "h3", "h4"]:
            out.append("")

    return "\n".join(out)


# ---------------------------------------------------------
# TOP-LEVEL EXTRACTOR
# ---------------------------------------------------------

def extract_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # strip scripts/styles and comments
    for j in soup(["script", "style"]):
        j.extract()
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    real_tables = extract_real_tables(soup)
    escaped_tables = extract_escaped_tables(soup)
    visible_text = extract_visible_text(soup)

    return real_tables, escaped_tables, visible_text


# ---------------------------------------------------------
# MAIN (single-file mode)
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to a single HTML file to clean")
    parser.add_argument("--output_dir", default="cleaned_html", help="Directory to write cleaned file")
    parser.add_argument("--output_name", default=None, help="Optional output filename (overrides default)")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output_dir
    output_name = args.output_name

    if not os.path.isfile(input_path):
        raise SystemExit(f"[ERROR] Input file not found: {input_path}")

    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    real_tables, escaped_tables, visible_text = extract_from_html(html)

    all_lines = []

    # Real tables first
    for t in real_tables:
        all_lines.append(t)
        all_lines.append("")

    # Escaped tables after
    for t in escaped_tables:
        all_lines.append(t)
        all_lines.append("")

    # Then the visible text
    all_lines.append(visible_text)

    cleaned = "\n".join(all_lines).strip()

    # Determine output filename
    if output_name:
        outname = output_name
    else:
        base = os.path.basename(input_path).rsplit(".", 1)[0]
        outname = base + "_clean.txt"

    outpath = os.path.join(output_dir, outname)

    with open(outpath, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"[OK] cleaned → {outpath}")


if __name__ == "__main__":
    main()
