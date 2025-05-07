import pandas as pd
import time
from schema import FEIJIU_BIDDING_LOW_LEVEL_COLUMNS
from ThirdPartyFetcher.constant.general_constants import HOME_DIR, skip_words
from ThirdPartyFetcher.utils.soup_utils import url_to_soup

high_level_bidding_path = f"{HOME_DIR}data/bidding/tp4_feijiu_high_level_bidding_Province_陕西_City_咸阳市_Status_仅招标_2025-04-30_to_2025-05-07.csv"

def get_bidding_details(high_level_path: str = high_level_bidding_path, max_limit: int = None):
    high_level_bid_df = pd.read_csv(high_level_path)
    max_limit = max_limit if max_limit else len(high_level_bid_df) + 1

    bidding_details = []
    for idx, row in high_level_bid_df.iterrows():
        if idx < max_limit:
            url = row['url']
            bid_soup = url_to_soup(url)

            # get announcement details
            desc = bid_soup.select_one('.content')
            announcement = desc.get_text(strip=True) if desc else ""
            for skip_word in skip_words:
                if skip_word in announcement:
                    announcement = announcement[:announcement.index(skip_word)]
            announcement = announcement.replace("\n", ";")

            # get keywords
            meta_tag = bid_soup.find('meta', attrs={'name': 'keywords'})
            keywords = meta_tag.get('content') if meta_tag else None

            bidding_details.append(dict(zip(FEIJIU_BIDDING_LOW_LEVEL_COLUMNS,
                                            [row["bidding_id"], row["date"], row["url"], row['province'], row['bid_or_ask'],
                                             row['status'], row["title"], keywords, announcement])))

            time.sleep(1)

    bidding_details_df = pd.DataFrame(bidding_details)
    bidding_details_df.to_csv(high_level_path.replace("high_level", "low_level"), index=False)
    print("Successfully saved low-level bidding details")

get_bidding_details()