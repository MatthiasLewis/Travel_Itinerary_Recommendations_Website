import pandas as pd
from shapely.geometry import Point

# 最高最低平均價格 vs 偏好價格
def calculate_price_score(lower_price, ceiling_price, pref_price ):
    avg_price = (lower_price + ceiling_price)/2
    if pref_price == 0 : diff_percent = avg_price
    else: diff_percent = abs(pref_price - avg_price) / pref_price
    minus_score = diff_percent * 100
    score = (100 - minus_score).apply(lambda x: max(0, x)).astype(int)
    return score


# 價格等級轉換金額 vs 偏好價格
def calculate_price_score_2(price_level, pref_price_level):
    minus_score = (price_level - pref_price_level).apply(lambda x: max(0,x))  # 4-3=1  3-5=0
    score = 100 - minus_score * 20
    return score

# 特徵重疊度
def calculate_tag_score(tag, pref_tag):
    def calculate_score(tags):
        if pd.notna(tags) and len(pref_tag)!=0:
            tags_set = set(tags.split(','))  # Convert comma-separated strings to sets
            common = tags_set.intersection(pref_tag)
            return max(20, int(len(common) / len(pref_tag) * 100))
        else:
            return 20
        
    score = tag.apply(calculate_score)
    return score

# 價格差異度(Shawn)
import numpy as np
def calculate_price_score_3(price_level, pref_price_level):
    price_diff = price_level - pref_price_level
    score = np.where(price_diff <= 0, 1, 1 - price_diff)
    return np.maximum(score, 0)  # 確保分數不為負值



# 每符合一個tag就加1分(Shawn)
def calculate_tag_score_2(tag, pref_tag):
    def calculate_score_2(tags):
        if pd.notna(tags):
            tags_set = set(tags.split(', '))  # Convert comma-separated strings to sets
            common = tags_set.intersection(pref_tag)
            return max(0, len(common))
        else:
            return 0
        
    score = tag.apply(calculate_score_2)
    return score

# 旅館價格(Shawn)
def calculate_hotel_score(min_price, max_price, user_price):
    price_rate = np.where(
        (min_price <= user_price) & (user_price <= max_price),
        (user_price - min_price) / (max_price - min_price),
        0
    )
    score = np.round(price_rate * 10, 1)
    return score

# 旅館價格(Winnie 0824)
def calculate_hotel_score_2(lower_price, ceiling_price, pref_price ):   # ***
    return (lower_price <= pref_price).astype(int)
