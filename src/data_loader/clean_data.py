import os
import pandas as pd

# BULL장 데이터셋
INPUT_FILENAME = "bull_1year_data.csv"
OUTPUT_FILENAME = "cleaned_bull_1year_data.csv"
CNT = 77

# BEAR장 데이터셋
# INPUT_FILENAME = "bear_1year_data.csv"
# OUTPUT_FILENAME = "cleaned_bear_1year_data.csv"
# CNT = ?

# 경로 지정 & 데이터 읽어오기
script_dir = os.path.dirname(os.path.abspath(__file__)) # ../data_loader
root_dir = os.path.dirname(os.path.dirname(script_dir)) # ../StockPrediction-AI
data_dir = os.path.join(root_dir, 'data') # ../data
data_path = os.path.join(data_dir, INPUT_FILENAME)
df = pd.read_csv(data_path)

# 불순물 데이터 지우기
df['DateTime'] = pd.to_datetime(df['DateTime'])
df['Date'] = df['DateTime'].dt.date
row_counts = df.groupby('Date').size()
valid_index = row_counts[row_counts == CNT].index
df.set_index('Date', inplace = True)
clean_data = df.loc[valid_index].copy()
clean_data.reset_index(inplace = True)
clean_data.drop(columns = 'Date', inplace = True)

# 삭제한 날짜 출력하기
invalid_dates = row_counts[row_counts != CNT]
print("=== 삭제된 불완전한 날짜 목록 ===")
for date, count in invalid_dates.items():
    print(f"날짜: {date} | 데이터 개수: {count}개 (정상: {CNT}개)")

# 정제 데이터 저장하기
clean_data_path = os.path.join(data_dir, OUTPUT_FILENAME)
clean_data.to_csv(clean_data_path, index = False, encoding = 'UTF-8')