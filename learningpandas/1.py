
import pandas as pd
import numpy as np



# 准备测试数据
df = pd.DataFrame({
    "姓名": ["张三", "李四", "王五"],
    "年龄": [25, 30, 28],
    "城市": ["北京", "上海", "广州"]
})


# 不写入索引
df.to_csv("output.csv", index=False)

print(df)

print(df.iloc[0,1])