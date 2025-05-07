import pandas as pd
import datetime
from bs4 import BeautifulSoup
from ThirdPartyFetcher.constant.general_constants import HOME_DIR
from filter_constant import PROVINCE_DICT, BID_OR_ASK_DICT, STATUS_DICT
from schema import FEIJIU_BIDDING_HIGH_LEVEL_COLUMNS
from ThirdPartyFetcher.utils.other_utils import get_bidding_id
from ThirdPartyFetcher.utils.soup_utils import url_to_soup

Feijiu_Search_Base_Url = "https://www.zbytb.com/search/"

def build_search_url(page: int = 1,
                     province: str = "陕西",
                     bid_or_ask: str = "仅招标",
                     status: str = "招标",
                     keyword: str = "" # example: "建筑"
                     ) -> str:
    params = {
        "page": page,
        "moduleid": STATUS_DICT.get(status, "25"),
        "areaids": PROVINCE_DICT.get(province, ""),
        "obiao": BID_OR_ASK_DICT.get(bid_or_ask, "0"),
        "field": "0",
        "okw": "",
        "zizhi": "",
        "search": "1",
        "kw": keyword,
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return Feijiu_Search_Base_Url + "?" + query_string


def get_single_page_bidding(soup: BeautifulSoup, province: str = None, bid_or_ask: str = None, status: str = None) -> list:
    results = []
    for div in soup.find_all("div", class_="title"):
        # Bidding_ID, date
        spans = div.find_all("span")
        date = None
        for sp in spans:
            if 'lszz' not in sp.get("class", []):
                date = str(datetime.date.today().year) + "-" + sp.get_text(strip=True)
                break  # we found the first date span
        bidding_id = get_bidding_id(date)

        # Url, Title
        a_tag = div.find("a")
        if a_tag:
            url = a_tag.get("href")
            title = a_tag.get_text(strip=True)
        else:
            url = None
            title = None

        # Comment
        span_lszz = div.find("span", class_="lszz")
        comment = span_lszz.get_text(strip=True) if span_lszz else None

        results.append(dict(zip(FEIJIU_BIDDING_HIGH_LEVEL_COLUMNS,
                                [bidding_id, date, url, province, bid_or_ask, status, title, comment])))

    return results


def get_all_page_bidding(province: str, bid_or_ask: str, status: str, stop_date: str = str(datetime.date.today())) -> list:
    page = 1
    keep_scraping = True
    all_bids = []

    while keep_scraping:
        page_url = build_search_url(page, province, bid_or_ask, status)

        print(f"Fetching page {page}: {page_url}")
        page_soup = url_to_soup(page_url)
        page_bid = get_single_page_bidding(page_soup, province, bid_or_ask, status)

        for bid in page_bid:
            if bid["date"] and bid["date"] < stop_date:
                print(f"Stopping at bid dated {bid['date']}")
                keep_scraping = False
                break
            all_bids.append(bid)

        if keep_scraping and len(page_bid) == 0:
            # No more bids on next page
            print("No more bids on next page.")
            keep_scraping = False
        elif keep_scraping:
            page += 1

    return all_bids

# todo: add functionality of past n week and past n month
all_page_bidding_data = get_all_page_bidding(province="陕西", bid_or_ask="仅招标", status="招标", stop_date = "2025-05-01")
all_page_bidding_df = pd.DataFrame(all_page_bidding_data)

# todo: to make the filename dynamically generated
all_page_bidding_df.to_csv(f"{HOME_DIR}data/bidding/tp4_feijiu_high_level_bidding_2025_05_01_to_2025_05_07.csv", index=False)
