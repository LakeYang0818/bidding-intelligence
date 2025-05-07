import requests
from bs4 import BeautifulSoup
import pandas as pd

HOME_DIR = "/Users/lakeyang/PycharmProjects/bidding-intelligence/"

tp_name = '中国招标投标公共服务平台'
tp_df = pd.read_csv(f"{HOME_DIR}data/source/third_party_platforms.csv", sep = "|")
tp_url = tp_df[tp_df['Platform_Name'] == tp_name]['URL'].values[0]

pseudo_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 1. Configure search parameters (Shaanxi + Scrap Metal)
default_params = {
    "category": "GCJS",  # 工程建设 (Construction)
    "industry": "09",  # 环保/再生资源 (Environment/Recycling)
    "region": "610000",  # Shaanxi Province code
}


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# 1. Configure Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

url = "https://bulletin.cebpubservice.com/xxfbcmses/search/bulletin.html?category=GCJS&industry=09&region=610000"
driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

tenders = []
for item in soup.select('.list-item'):
    tenders.append({
        'Title': item.select_one('.title').text.strip(),
        'Date': item.select_one('.publish-time').text.strip(),
        'Link': item.find('a')['href']
    })
print(tenders)

def fetch_all_tenders(start_date: str, url: str = tp_url, params: dict = default_params, headers: dict = pseudo_headers):
    all_tenders = []

    params = params
    params['start_date'] = start_date

    while True:
        try:
            print(f"Accessing {url}")
            response = requests.get(url)
            response.raise_for_status()
            print(response.content)
            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup.prettify())

            data = response.json()
            print(type(data))
            print(len(data))

            if not data.get("data", {}).get("records"):
                break

            for item in data["data"]["records"]:
                all_tenders.append({
                    "公告标题": item.get("title"),
                    "项目编号": item.get("projectCode"),
                    "发布时间": item.get("publishTime"),
                    "截止时间": item.get("bidEndTime"),
                    "招标人": item.get("tenderer"),
                    "预算金额": item.get("budget", "N/A"),
                    "省份": item.get("regionName"),
                    "详情链接": f"https://bulletin.cebpubservice.com/xxfbcmses/detail/{item['id']}.html"
                })

        except Exception as e:
            print(f"Error: {e}")
            break

    return all_tenders


start_date = "2025-03-30"
tenders = fetch_all_tenders(start_date)
if tenders:
    df = pd.DataFrame(tenders)
    # Convert date columns to datetime for sorting
    df["发布时间"] = pd.to_datetime(df["发布时间"])
    df["截止时间"] = pd.to_datetime(df["截止时间"])
    # Sort by publish date (newest first)
    df = df.sort_values("发布时间", ascending=False)

    filename = f"tenders_from_{start_date}.csv"
    df.to_csv(filename, index=False, encoding="utf_8_sig")
    print(f"Successfully saved {len(tenders)} tenders to {filename}")
    print(f"Date range: {df['发布时间'].min().date()} to {df['发布时间'].max().date()}")
else:
    print("No tenders found for the given filters.")