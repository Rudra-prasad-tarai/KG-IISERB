import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def scrape_iiser_students(url):
    """
    Scrape PhD student information from IISER Bhopal website
    """
    try:
        # Send GET request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        students = []
        
        # Find all student entries (adjust selectors based on actual HTML structure)
        # Looking for div/section elements containing student info
        student_sections = soup.find_all(['div', 'section'], class_=lambda x: x and ('student' in x.lower() or 'profile' in x.lower()))
        
        # Alternative: Find by link patterns
        if not student_sections:
            # Find all links that might be student names
            name_links = soup.find_all('a', href=True)
            
            for link in name_links:
                name = link.get_text(strip=True)
                # Skip navigation links
                if name and len(name) > 3 and not any(skip in name.lower() for skip in ['skip', 'menu', 'navigation', 'home', 'search']):
                    # Try to find associated info
                    parent = link.find_parent(['div', 'section', 'article'])
                    if parent:
                        info = {
                            'name': name,
                            'url': link.get('href'),
                            'email': None,
                            'year_of_joining': None,
                            'supervisor': None
                        }
                        
                        # Extract email
                        email_link = parent.find('a', href=lambda x: x and 'mailto:' in x)
                        if email_link:
                            info['email'] = email_link.get('href').replace('mailto:', '')
                        
                        # Extract text content for year and supervisor
                        text = parent.get_text()
                        if 'Year of Joining' in text or 'Joining' in text:
                            lines = [l.strip() for l in text.split('\n') if l.strip()]
                            for i, line in enumerate(lines):
                                if 'joining' in line.lower() and i + 1 < len(lines):
                                    info['year_of_joining'] = lines[i + 1]
                                if 'supervisor' in line.lower() and i + 1 < len(lines):
                                    info['supervisor'] = lines[i + 1]
                        
                        students.append(info)
        
        # Remove duplicates based on name
        seen = set()
        unique_students = []
        for student in students:
            if student['name'] not in seen and len(student['name']) > 5:
                seen.add(student['name'])
                unique_students.append(student)
        
        return unique_students
    
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def save_to_csv(students, filename='iiser_phd_students.csv'):
    """Save student data to CSV"""
    df = pd.DataFrame(students)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df

def save_to_json(students, filename='iiser_phd_students.json'):
    """Save student data to JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")

# Main execution
if __name__ == "__main__":
    url = "https://dsestudents.iiserb.ac.in"
    
    print("Scraping IISER Bhopal PhD Students data...")
    students = scrape_iiser_students(url)
    
    if students:
        print(f"\nFound {len(students)} students")
        print("\nStudent Names:")
        for i, student in enumerate(students, 1):
            print(f"{i}. {student['name']}")
            if student['email']:
                print(f"   Email: {student['email']}")
            if student['supervisor']:
                print(f"   Supervisor: {student['supervisor']}")
            print()
        
        # Save to files
        save_to_csv(students)
        save_to_json(students)
        
        # Display as DataFrame
        df = pd.DataFrame(students)
        print("\nDataFrame Preview:")
        print(df.to_string())
    else:
        print("No students found. The page structure might be different.")
        print("Please check the HTML structure manually.")