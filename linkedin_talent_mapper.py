
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re

def login_to_linkedin(page, username, password):
    page.goto("https://www.linkedin.com/login")
    page.fill('input#username', username)
    page.fill('input#password', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(5000)

def go_to_company_people_page(page, company_name):
    company_slug = company_name.lower().replace(" ", "")
    page.goto(f"https://www.linkedin.com/company/{company_slug}/people/")
    page.wait_for_timeout(5000)

def apply_filters(page):
    try:
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
    except:
        pass  # fallback in case filters aren't available

def extract_college_year(text):
    college_match = re.search(r"(IIT|NIT|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text)
    year_match = re.search(r'(\d{4})\s?[-–]\s?(\d{4})', text)
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
        page.set_default_timeout(60000)
        login_to_linkedin(page, username, password)
        go_to_company_people_page(page, company_name)
        apply_filters(page)
        profiles = extract_profiles(page)
        save_profiles(profiles)
        browser.close()
