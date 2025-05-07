import pandas as pd
import datetime
from bs4 import BeautifulSoup
from ThirdPartyFetcher.constant.general_constants import HOME_DIR
from filter_constant import PROVINCE_DICT, PROVINCE_CITY_DICT, BID_OR_ASK_DICT, STATUS_DICT
from schema import FEIJIU_BIDDING_HIGH_LEVEL_COLUMNS
from ThirdPartyFetcher.utils.other_utils import get_bidding_id
from ThirdPartyFetcher.utils.soup_utils import url_to_soup

Feijiu_Search_Base_Url = "https://www.zbytb.com/search/"


def build_search_url(page: int, province: str, city: str, bid_or_ask: str, status: str, keyword: str) -> str:
    province_area_id = PROVINCE_DICT.get(province, "") if province else ""
    city_area_id = PROVINCE_CITY_DICT.get(province, "").get(city, "") if city else None
    print(city_area_id)
    params = {
        "page": page,
        "moduleid": STATUS_DICT.get(status, "25"),
        "areaids": city_area_id if city_area_id else province_area_id,
        "obiao": BID_OR_ASK_DICT.get(bid_or_ask, "0"),
        "field": "0",
        "okw": "",
        "zizhi": "",
        "search": "1",
        "kw": keyword,
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return Feijiu_Search_Base_Url + "?" + query_string


def get_single_page_bidding(soup: BeautifulSoup, province: str, city: str, bid_or_ask: str, status: str) -> list:
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
                                [bidding_id, date, url, province, city, bid_or_ask, status, title, comment])))

    return results


def get_stop_date(n: int, unit: str = "week") -> str:
    today = datetime.date.today()
    if unit == "week":
        past_date = today - datetime.timedelta(weeks=n)
    elif unit == "month":
        past_date = today - datetime.timedelta(days=30 * n)
    else:
        raise ValueError("unit must be 'week' or 'month'")
    return past_date.isoformat()


def construct_high_level_feijiu_path(province: str, city: str, bid_or_ask: str, start_date: str, end_date: str):
    return f"{HOME_DIR}data/bidding/tp4_feijiu_high_level_bidding_Province_{province}_City_{city}_Status_{bid_or_ask}_{start_date}_to_{end_date}.csv"


def get_all_page_bidding(province: str = "陕西",
                         city: str = "咸阳市",
                         bid_or_ask: str = "仅招标",
                         status: str = "招标",
                         keyword: str = "",  # example: "建筑"
                         specified_stop_date: str = None, past_n_week: int = None, past_n_months: int = None) -> list:
    # get stop date
    if specified_stop_date:
        stop_date = specified_stop_date
    elif past_n_week:
        stop_date = get_stop_date(past_n_week, "week")
    elif past_n_months:
        stop_date = get_stop_date(past_n_months, "month")
    else:
        stop_date = str(datetime.date.today())

    page = 1
    keep_scraping = True
    all_bids = []

    while keep_scraping:
        page_url = build_search_url(page = page,
                                    province = province,
                                    city = city,
                                    bid_or_ask = bid_or_ask,
                                    status = status,
                                    keyword = keyword)

        print(f"Fetching page {page}: {page_url}")
        page_soup = url_to_soup(page_url)
        page_bid = get_single_page_bidding(soup = page_soup,
                                           province = province,
                                           city = city,
                                           bid_or_ask = bid_or_ask,
                                           status = status)

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

    all_bids_df = pd.DataFrame(all_bids)
    all_bids_df.to_csv(construct_high_level_feijiu_path(province, city, bid_or_ask, stop_date, str(datetime.date.today())),
                       index=False)
    print("Successfully fetched all bids.")


get_all_page_bidding(province="陕西",
                     city = "咸阳市",
                     bid_or_ask="仅招标",
                     status="招标",
                     past_n_week = 1,
                     #specified_stop_date = "2025-05-01" # fetch data until this date,
                     #past_n_week = 1, # fetch data until past n weeks
                     #past_n_month = 1, # fetch data until past n months
                     )