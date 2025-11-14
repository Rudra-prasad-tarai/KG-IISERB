import requests
from bs4 import BeautifulSoup

def fetch_and_save_html(url, filename='webpage.html'):
    """
    Fetch HTML from URL and save to file
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"Fetching HTML from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Save raw HTML
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✓ HTML saved to: {filename}")
        print(f"✓ File size: {len(response.text)} characters")
        
        # Pretty print with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        pretty_html = soup.prettify()
        
        pretty_filename = filename.replace('.html', '_pretty.html')
        with open(pretty_filename, 'w', encoding='utf-8') as f:
            f.write(pretty_html)
        
        print(f"✓ Pretty HTML saved to: {pretty_filename}")
        
        # Print preview
        print("\n" + "="*50)
        print("HTML PREVIEW (first 1000 characters):")
        print("="*50)
        print(response.text[:1000])
        print("...")
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching HTML: {e}")
        return None

if __name__ == "__main__":
    url = "https://dsestudents.iiserb.ac.in"
    html_content = fetch_and_save_html(url, 'iiser_bhopal.html')