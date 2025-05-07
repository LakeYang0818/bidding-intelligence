import pandas as pd

bid_details_path = 'data/bidding/tp4_feijiu_low_level_bidding_Province_陕西_City_咸阳市_Status_仅招标_2025-04-30_to_2025-05-07.csv'
bid_details_df = pd.read_csv(bid_details_path)

bid_details_in_mandarin_path = 'data/bidding/招标公告_陕西省_咸阳市_招标_2025年04月30日_至_2025年05月07日.csv'
bid_details_in_mandarin_df = bid_details_df[['date', 'status', 'url', 'province', 'city', 'title', 'comment']]
bid_details_in_mandarin_df.columns = ["发布日期", "招标状态", "网站链接", "省份", "城市", "标题", "招标公告"]
bid_details_in_mandarin_df.to_csv(bid_details_in_mandarin_path, index=False)

