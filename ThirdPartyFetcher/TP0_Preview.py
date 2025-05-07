import pandas as pd
pd.set_option('display.width', None)
pd.set_option('display.max_columns', None)


TP_SOURCE = 'data/source/third_party_platforms.csv'
tp_df = pd.read_csv(TP_SOURCE, sep='|')
print("Preview all Third Party Tenderee Sources")
print(tp_df)

