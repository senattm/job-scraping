import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import time
import random


def scrape(maxPages=25, pageSize=10, sleepSeconds=1.2):
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    
    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/143.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    })

    baseParams = {
    "keywords": '"Yazılım" OR "Software" OR "Developer" OR "Geliştirici" OR '
    '"Mühendisi" OR "Full Stack" OR "Backend" OR "Frontend"', 
    "location": "Turkey"
}

    whitelist = [
        "yazılım", "software", "developer", "geliştirici", "mühendis", 
        "engineer", "full stack", "backend", "frontend", "staj", "intern",
        "mobile", "ios", "android", "data", "analyst", "test", "qa"
    ] 

    seen = set() 
    totalPrinted = 0

    try:
        for page in range(maxPages):
            start = page * pageSize
            params = dict(baseParams)
            params["start"] = start

            response = session.get(
                url,
                params=params,
                timeout=(5, 20),  
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            jobs = soup.find_all("li")

            if not jobs:
                print(f"No results")
                break

            for job in jobs:
                titleTag = job.find("h3", class_="base-search-card__title")
                companyTag = job.find("h4", class_="base-search-card__subtitle")
                dateTag = job.find("time")
                linkTag = job.find("a", class_="base-card__full-link")

                if not titleTag:
                    continue
                
                title = titleTag.get_text(strip=True)
                title_lower = title.lower()
                if not any(keyword in title_lower for keyword in whitelist):
                    continue

                company = companyTag.get_text(strip=True) if companyTag else "no company name"
                date = dateTag.get("datetime") if dateTag else "date not specified"
                link = linkTag.get("href") if linkTag else "link not found"

                if link in seen:
                    continue
                seen.add(link)

                print(f"Job: {title}")
                print(f"Company: {company}")
                print(f"Date: {date}")
                print(f"Link: {link}")
                print("-" * 20)

                totalPrinted += 1

            print(f"Batch start={start}\n")

            time.sleep(random.uniform(sleepSeconds * 0.7, sleepSeconds * 1.3))


        print(f"\nTotal found {totalPrinted}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    finally:
        session.close()
        print("Session closed")


if __name__ == "__main__":
    scrape()
