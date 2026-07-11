import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from database import supabase
from config import (
    LINKEDIN_SEARCH_QUERIES, LINKEDIN_LOCATION, LINKEDIN_GEO_ID,
    LINKEDIN_JOB_TYPE, LINKEDIN_JOB_POSTING_DATE, LINKEDIN_F_WT,
    LINKEDIN_MAX_START, MAX_JOBS_PER_SEARCH,
    REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY_SECONDS, JOBS_TABLE
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]


def convert_html_to_markdown(html: str) -> str:
    if not html or not html.strip():
        return ""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all(['script', 'style', 'nav',
                                   'footer', 'header', 'iframe', 'noscript']):
            tag.decompose()
        markdown = md(str(soup), heading_style="ATX",
                      bullets="-", strip=['img'])
        lines, result, prev_blank = markdown.splitlines(), [], False
        for line in lines:
            if not line.strip():
                if not prev_blank:
                    result.append('')
                prev_blank = True
            else:
                result.append(line)
                prev_blank = False
        return '\n'.join(result).strip()
    except Exception as e:
        logging.error(f"HTML to markdown error: {e}")
        return ""


def get_existing_job_ids() -> set:
    existing = set()
    offset   = 0
    while True:
        res = supabase.table(JOBS_TABLE)\
            .select("job_id")\
            .range(offset, offset + 999)\
            .execute()
        if not res.data:
            break
        for row in res.data:
            existing.add(str(row["job_id"]))
        if len(res.data) < 1000:
            break
        offset += 1000
    logging.info(f"Found {len(existing)} existing jobs in DB")
    return existing


def fetch_linkedin_job_ids(query: str, location: str) -> list:
    job_ids = []
    start   = 0

    while start <= LINKEDIN_MAX_START:
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={query.replace(' ', '%20')}"
            f"&location={location}"
            f"&geoId={LINKEDIN_GEO_ID}"
            f"&f_TPR={LINKEDIN_JOB_POSTING_DATE}"
            f"&f_JT={LINKEDIN_JOB_TYPE}"
            f"&f_WT={LINKEDIN_F_WT}"
            f"&start={start}"
        )

        if start > 0:
            time.sleep(random.uniform(5.0, 15.0))

        headers = {'User-Agent': random.choice(USER_AGENTS)}
        res     = None
        retries = 0

        while retries <= MAX_RETRIES:
            try:
                res = requests.get(url, headers=headers,
                                   timeout=REQUEST_TIMEOUT)
                res.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and retries < MAX_RETRIES:
                    retries += 1
                    wait = RETRY_DELAY_SECONDS + random.uniform(0, 5)
                    logging.warning(f"Rate limited. Retrying in {wait:.0f}s")
                    time.sleep(wait)
                    headers = {'User-Agent': random.choice(USER_AGENTS)}
                else:
                    res = None
                    break
            except Exception as e:
                logging.error(f"Request error: {e}")
                res = None
                break

        if not res or not res.text:
            break

        soup  = BeautifulSoup(res.text, 'html.parser')
        items = soup.find_all('li')
        if not items:
            break

        added = 0
        for item in items:
            card = item.find("div", {"class": "base-card"})
            urn  = card.get('data-entity-urn') if card else None
            if urn and 'jobPosting:' in urn:
                try:
                    jid = urn.split(":")[3]
                    if jid not in job_ids:
                        job_ids.append(jid)
                        added += 1
                except IndexError:
                    pass

        logging.info(f"Page start={start}: {added} job IDs added")
        if added == 0:
            break
        start += 10

    return job_ids


def fetch_linkedin_job_details(job_id: str) -> dict | None:
    url     = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    headers = {'User-Agent': random.choice(USER_AGENTS)}

    time.sleep(random.uniform(3.0, 8.0))

    retries = 0
    resp    = None
    while retries <= MAX_RETRIES:
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and retries < MAX_RETRIES:
                retries += 1
                time.sleep(RETRY_DELAY_SECONDS + random.uniform(0, 5))
                headers = {'User-Agent': random.choice(USER_AGENTS)}
            else:
                return None
        except Exception:
            return None

    if not resp:
        return None

    try:
        soup    = BeautifulSoup(resp.text, 'html.parser')
        details = {"job_id": job_id}

        # Company
        try:
            img = soup.find("div", {"class": "top-card-layout__card"})\
                      .find("a").find("img")
            details["company"] = img.get('alt', '').strip() if img else None
            if not details["company"]:
                link = soup.find("a", {"class": "topcard__org-name-link"})
                details["company"] = link.text.strip() if link else None
        except Exception:
            details["company"] = None

        # Title
        try:
            t = soup.find("div", {"class": "top-card-layout__entity-info"}).find("a")
            details["job_title"] = t.text.strip() if t else None
        except Exception:
            details["job_title"] = None

        # Level
        try:
            criteria = soup.find("ul", {"class": "description__job-criteria-list"})\
                           .find_all("li")
            details["level"] = None
            for item in criteria:
                h = item.find("h3", {"class": "description__job-criteria-subheader"})
                if h and "Seniority" in h.text:
                    span = item.find("span", {"class": "description__job-criteria-text"})
                    details["level"] = span.text.strip() if span else None
        except Exception:
            details["level"] = None

        # Location
        try:
            loc = soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"})
            details["location"] = loc.text.strip() if loc else None
        except Exception:
            details["location"] = None

        # Description
        try:
            desc_div = soup.find("div", {"class": "show-more-less-html__markup"})
            desc_html = str(desc_div) if desc_div else ""
            details["description"] = convert_html_to_markdown(desc_html) if desc_html else None
        except Exception:
            details["description"] = None

        details["provider"] = "linkedin"
        return details

    except Exception as e:
        logging.error(f"Error parsing job {job_id}: {e}")
        return None


def save_jobs(jobs: list) -> int:
    saved = 0
    for job in jobs:
        try:
            supabase.table(JOBS_TABLE)\
                .upsert(job, on_conflict="job_id")\
                .execute()
            saved += 1
        except Exception as e:
            logging.error(f"Error saving job {job.get('job_id')}: {e}")
    return saved


def run_scraper(
    queries:  list = None,
    location: str  = None,
    limit:    int  = None
) -> dict:
    queries  = queries  or LINKEDIN_SEARCH_QUERIES
    location = location or LINKEDIN_LOCATION
    limit    = limit    or MAX_JOBS_PER_SEARCH

    existing     = get_existing_job_ids()
    total_saved  = 0
    summary      = []

    for query in queries:
        logging.info(f"Scraping: '{query}' in {location}")

        all_ids = fetch_linkedin_job_ids(query, location)
        new_ids = [j for j in all_ids if j not in existing][:limit]

        logging.info(f"{len(all_ids)} total, {len(new_ids)} new")

        if not new_ids:
            summary.append({"query": query, "new_jobs": 0})
            continue

        jobs_data = []
        for jid in new_ids:
            details = fetch_linkedin_job_details(jid)
            if details and details.get("description"):
                jobs_data.append(details)
                existing.add(jid)

        saved = save_jobs(jobs_data)
        total_saved += saved
        summary.append({"query": query, "new_jobs": saved})
        logging.info(f"Saved {saved} jobs for '{query}'")

    return {
        "total_saved": total_saved,
        "summary":     summary,
        "queries_run": len(queries)
    }


if __name__ == "__main__":
    result = run_scraper()
    print(f"\nDone: {result['total_saved']} new jobs saved")
    for s in result['summary']:
        print(f"  {s['query']}: {s['new_jobs']} jobs")
