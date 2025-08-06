# linkedin_talent_mapper.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def login_to_linkedin(page, username, password):
    page.goto("https://www.linkedin.com/login")
    page.fill('input#username', username)
    page.fill('input#password', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(5000)

def go_to_company_people_page(page, company_name):
    search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name}"
    page.goto(search_url)
    page.wait_for_timeout(3000)
    page.click("div.entity-result__content")
    page.wait_for_timeout(3000)
    page.click("a[href*='/people/']")
    page.wait_for_timeout(5000)

def apply_filters(page):
    page.click('button:has-text("Locations")')
    page.fill('input[placeholder="Add a location"]', "India")
    page.click('text="India"')
    page.click('button:has-text("Show results")')
    page.wait_for_timeout(3000)

    page.click('button:has-text("What they do")')
    page.fill('input[placeholder="Add a function"]', "Engineering")
    page.click('text="Engineering"')
    page.click('button:has-text("Show results")')
    page.wait_for_timeout(5000)

def extract_college_year(text):
    college_match = re.search(r"(IIT|NIT|[A-Z][a-z]+(?:\\s[A-Z][a-z]+)*)", text)
    year_match = re.search(r'(\\d{4})\\s?[-\u2013]\\s?(\\d{4})', text)
    college = college_match.group(0) if college_match else "Unknown"
    grad_year = year_match.group(2) if year_match else "Unknown"
    return college, grad_year

def extract_profiles(page):
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    profiles = []
    for profile_card in soup.find_all('li', class_='reusable-search__result-container'):
        try:
            name = profile_card.find('span', class_='entity-result__title-text').get_text().strip()
            profile_url = profile_card.find('a', href=True)['href']
            subtitle = profile_card.find('div', class_='entity-result__secondary-subtitle').get_text()
            college, grad_year = extract_college_year(subtitle)
            profiles.append({
                'name': name,
                'url': f"https://www.linkedin.com{profile_url}",
                'college': college,
                'grad_year': grad_year
            })
        except Exception:
            continue
    return profiles

def save_profiles(profiles):
    data = []
    for p in profiles:
        name_with_link = f'=HYPERLINK("{p["url"]}", "{p["name"]}")'
        data.append([name_with_link, p["college"], p["grad_year"]])
    df = pd.DataFrame(data, columns=["Candidate", "College", "Graduation Year"])
    df.to_excel("Talent_Map.xlsx", index=False)

def run_tool(company_name, username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login_to_linkedin(page, username, password)
        go_to_company_people_page(page, company_name)
        apply_filters(page)
        profiles = extract_profiles(page)
        save_profiles(profiles)
        print("Talent map saved as Talent_Map.xlsx")
        browser.close()

# Example usage:
# run_tool("Google", "your_email", "your_password")
