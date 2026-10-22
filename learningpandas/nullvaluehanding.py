import pandas as pd

df = pd.read_csv("property-data.csv")

# 将原先的 df["ST_NUM"].fillna(x, inplace = True) 替换为下式：
df["ST_NUM"] = df["ST_NUM"].fillna(df["ST_NUM"].median())
df.fillna
print(df.to_string())