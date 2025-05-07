from bs4 import BeautifulSoup
import pandas as pd
from schema import BIDDING_OPPORTUNITY_COLUMNS
from ThirdPartyFetcher.constant.general_constants import HOME_DIR
from ThirdPartyFetcher.utils.other_utils import get_bidding_id
from ThirdPartyFetcher.utils.soup_utils import url_to_soup

feijiu_name = 'Feijiu网'
feijiu_df = pd.read_csv(f"{HOME_DIR}data/source/third_party_platforms.csv", sep = "|")
feijiu_url = feijiu_df[feijiu_df['Platform_Name'] == feijiu_name]['URL'].values[0]
materials_url = feijiu_url + "v1/"

def get_bidding(soup: BeautifulSoup) -> list:
    data = []
    # get subpage from the navigator soup
    ## find any <li> element that is inside a <ul> that is inside an element with class pdbox (dot . stands for a class)
    for li in soup.select('.pdbox ul li'):
        # Can get Date, Title, Url info from subpage overview
        ## select the first time of a <span> element that has the class fr
        date = li.select_one('span.fr').text.strip()
        bidding_id = get_bidding_id(date)
        a_tag = li.select_one('a')
        title = a_tag.text.strip()
        url = a_tag['href']

        # visit the specific url to get details
        detail_soup = url_to_soup(url)
        keywords, announcement = get_bidding_details(detail_soup)
        bidding_data = [bidding_id, title, date, url, keywords, announcement]
        data.append(dict(zip(BIDDING_OPPORTUNITY_COLUMNS, bidding_data)))

    return data


def get_bidding_details(bidding_soup: BeautifulSoup):
    try: keywords = bidding_soup.select_one('meta[name="keywords"]')['content']
    except Exception: keywords = ""

    try: announcement = bidding_soup.select_one('meta[name="description"]')['content']
    except Exception: announcement = ""

    return keywords, announcement

materials_soup = url_to_soup(materials_url)
materials_data = get_bidding(materials_soup)
materials_df = pd.DataFrame(materials_data)
materials_df.to_csv(f"{HOME_DIR}data/bidding/tp4_feijiu_05072025.csv", index=False)
