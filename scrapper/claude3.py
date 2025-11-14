import requests
from bs4 import BeautifulSoup
import time

def fetch_and_save_html(url, filename='webpage.html'):
    """
    Fetch HTML from URL and save to file with multiple retry strategies
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Try different URL variations
    urls_to_try = [
        url,
        url.replace('https://', 'http://'),
        'https://www.iiserb.ac.in/dse-students',
        'http://dsestudents.iiserb.ac.in'
    ]
    
    for attempt_url in urls_to_try:
        try:
            print(f"\nAttempting: {attempt_url}")
            
            # Add timeout and allow redirects
            response = requests.get(
                attempt_url, 
                headers=headers, 
                timeout=10,
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            
            # Save raw HTML
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✓ SUCCESS! HTML saved to: {filename}")
            print(f"✓ File size: {len(response.text)} characters")
            print(f"✓ Status code: {response.status_code}")
            
            # Pretty print with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            pretty_html = soup.prettify()
            
            pretty_filename = filename.replace('.html', '_pretty.html')
            with open(pretty_filename, 'w', encoding='utf-8') as f:
                f.write(pretty_html)
            
            print(f"✓ Pretty HTML saved to: {pretty_filename}")
            
            # Extract and print student names if found
            print("\n" + "="*60)
            print("SEARCHING FOR STUDENT NAMES...")
            print("="*60)
            
            # Find links that look like names
            links = soup.find_all('a', href=True)
            student_names = []
            
            for link in links:
                text = link.get_text(strip=True)
                # Filter for names (contains "Mr." or "Ms." or looks like a name)
                if any(prefix in text for prefix in ['Mr.', 'Ms.', 'Dr.']):
                    student_names.append(text)
            
            if student_names:
                print(f"\nFound {len(student_names)} potential student names:")
                for i, name in enumerate(student_names, 1):
                    print(f"  {i}. {name}")
            else:
                print("No obvious student name patterns found.")
            
            # Print HTML preview
            print("\n" + "="*60)
            print("HTML PREVIEW (first 2000 characters):")
            print("="*60)
            print(response.text[:2000])
            print("\n... (truncated)")
            
            return response.text
            
        except requests.exceptions.SSLError as e:
            print(f"✗ SSL Error: {e}")
            print("  Try using HTTP instead of HTTPS")
            
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection Error: {e}")
            print("  The server might be down or requires VPN/institutional access")
            
        except requests.exceptions.Timeout as e:
            print(f"✗ Timeout Error: {e}")
            print("  Server took too long to respond")
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}")
        
        time.sleep(1)  # Wait between attempts
    
    print("\n" + "="*60)
    print("MANUAL ALTERNATIVES:")
    print("="*60)
    print("1. Try accessing from IISER network/VPN")
    print("2. Use browser to save HTML:")
    print("   - Open page in browser")
    print("   - Right-click → 'Save Page As' → 'Webpage, Complete'")
    print("   - Or press Ctrl+S")
    print("3. Use browser DevTools:")
    print("   - Press F12 → Console tab")
    print("   - Run: copy(document.documentElement.outerHTML)")
    print("   - Paste into a text file")
    print("\nOnce you have the HTML file, run:")
    print("  python3 scrapper/parse_html.py your_file.html")
    
    return None

def parse_local_html(filepath):
    """
    Parse HTML from a local file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print(f"\n✓ Loaded HTML from: {filepath}")
        print(f"✓ File size: {len(html_content)} characters")
        
        # Extract student information
        links = soup.find_all('a', href=True)
        students = []
        
        for link in links:
            text = link.get_text(strip=True)
            if any(prefix in text for prefix in ['Mr.', 'Ms.', 'Dr.']):
                students.append({
                    'name': text,
                    'url': link.get('href', '')
                })
        
        print(f"\nFound {len(students)} students:")
        for i, student in enumerate(students, 1):
            print(f"  {i}. {student['name']}")
        
        return students
        
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # If file path provided, parse local HTML
        print("Parsing local HTML file...")
        parse_local_html(sys.argv[1])
    else:
        # Try to fetch from URL
        url = "https://dsestudents.iiserb.ac.in"
        fetch_and_save_html(url, 'iiser_bhopal.html')