import os
import matplotlib.pyplot as plt
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__)) # ../src/utils
root_dir = os.path.dirname(os.path.dirname(script_dir)) # ../StockPrediction-AI
data_dir = os.path.join(root_dir, 'data')               # ../data
data_path = os.path.join(data_dir, "cleaned_bull_1year_data.csv")

df = pd.read_csv(data_path)

# 하루치로 resample하기
df['DateTime'] = pd.to_datetime(df['DateTime'])
df.set_index('DateTime', inplace=True)

df_daily = df.resample('D').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

# 주말 제거
df_daily.dropna(inplace=True)

# 변수 선언
x = df_daily.index
y1 = df_daily['Open']
y2 = df_daily['Close']
y3 = df_daily['High']
y4 = df_daily['Low']
y5 = df_daily['Volume']

plt.figure(figsize=(14, 8))

plt.suptitle('Daily Trend Analysis of Stock Data', fontsize=18, fontweight='bold')

# 시가
plt.subplot(2, 3, 1)
plt.plot(x, y1, color='orange', linewidth=1.5)
plt.title('Open')
plt.xticks(rotation=45)

# 종가
plt.subplot(2, 3, 2)
plt.plot(x, y2, color='blue', linewidth=1.5)
plt.title('Close')
plt.xticks(rotation=45)

# 고가
plt.subplot(2, 3, 3)
plt.plot(x, y3, color='red', linewidth=1.5)
plt.title('High')
plt.xticks(rotation=45)

# 저가
plt.subplot(2, 3, 4)
plt.plot(x, y4, color='green', linewidth=1.5)
plt.title('Low')
plt.xticks(rotation=45)

# 거래량
plt.subplot(2, 3, 5)
plt.bar(x, y5, color='gray', width=0.6)
plt.title('Volume')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()