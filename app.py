import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random
import pandas as pd

# ----------------- HELPERS -----------------
def normalize_url(url: str) -> str:
    return url.strip().lower()

def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:[\w-]+\.)+[a-zA-Z]{2,}'  # domain
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def fetch_html(url: str):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return response.text
    except Exception as e:
        return None
    return None

# ----------------- ON-PAGE ANALYSIS -----------------
def analyze_onpage(url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    results = {}

    # Title
    title = soup.title.string if soup.title else ""
    results["Title"] = title
    results["Title Length"] = len(title)

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc = meta_desc["content"] if meta_desc else ""
    results["Meta Description"] = desc
    results["Meta Desc Length"] = len(desc)

    # H1 Tags
    h1_tags = [h.get_text() for h in soup.find_all("h1")]
    results["H1 Tags"] = h1_tags
    results["H1 Count"] = len(h1_tags)

    # Word Count
    text = soup.get_text()
    words = text.split()
    results["Word Count"] = len(words)

    return results

# ----------------- OFF-PAGE ANALYSIS -----------------
def analyze_offpage(url: str):
    # Dummy values (in real world, API needed like Ahrefs, SEMrush)
    results = {
        "Backlinks": random.randint(50, 500),
        "Referring Domains": random.randint(10, 100),
        "Social Shares": random.randint(20, 1000),
    }
    return results

# ----------------- TECHNICAL ANALYSIS -----------------
def analyze_technical(url: str):
    base = url.rstrip("/")
    results = {}

    # Robots.txt check
    try:
        r = requests.get(base + "/robots.txt", timeout=5)
        results["robots.txt Found"] = (r.status_code == 200)
    except:
        results["robots.txt Found"] = False

    # Sitemap check
    try:
        s = requests.get(base + "/sitemap.xml", timeout=5)
        results["sitemap.xml Found"] = (s.status_code == 200)
    except:
        results["sitemap.xml Found"] = False

    # Page Speed (Dummy)
    results["Page Speed Score"] = random.randint(60, 100)

    # Mobile Friendly (Dummy)
    results["Mobile Friendly"] = random.choice([True, False])

    return results

# ----------------- MAIN PIPELINE -----------------
def run_pipeline(url: str):
    url = normalize_url(url)
    if not is_valid_url(url):
        return {"Error": "Invalid URL"}

    html = fetch_html(url)
    if not html:
        return {"Error": "Could not fetch website"}

    results = {}
    results["On-Page SEO"] = analyze_onpage(url, html)
    results["Off-Page SEO"] = analyze_offpage(url)
    results["Technical SEO"] = analyze_technical(url)

    return results

# ----------------- STREAMLIT APP -----------------
st.set_page_config(page_title="SEO Multi-Agent Analyzer", page_icon="🔎", layout="centered")

st.title("🔎 SEO Multi-Agent Analyzer")

url_input = st.text_input("Enter website URL (with http/https):", "")

if st.button("Analyze"):
    if url_input:
        results = run_pipeline(url_input)

        if "Error" in results:
            st.error(results["Error"])
        else:
            st.subheader("✅ On-Page SEO Results")
            st.json(results["On-Page SEO"])

            st.subheader("🔗 Off-Page SEO Results")
            st.json(results["Off-Page SEO"])

            st.subheader("⚙️ Technical SEO Results")
            st.json(results["Technical SEO"])

            # Convert to DataFrame for export
            all_data = []
            for section, data in results.items():
                for k, v in data.items():
                    all_data.append({"Category": section, "Metric": k, "Value": v})
            df = pd.DataFrame(all_data)
            st.dataframe(df)

    else:
        st.warning("⚠️ Please enter a valid URL to analyze.")
