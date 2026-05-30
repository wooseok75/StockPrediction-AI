import os
import matplotlib.pyplot as plt
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__)) # ../data_loader
root_dir = os.path.dirname(os.path.dirname(script_dir)) # ../StockPrediction-AI
data_dir = os.path.join(root_dir, 'data') # ../data
data_path = os.path.join(data_dir, "cleaned_bull_1year_data.csv")
df = pd.read_csv(data_path)

x = df['DateTime'].index
y1 =  df['Open']
y2 = df['Close']
y3 = df['High']
y4 = df['Low']
y5 = df['Volume']
plt.subplot(2, 3, 1)
plt.plot(x, y1)
plt.subplot(2, 3, 2)
plt.plot(x, y2)
plt.subplot(2, 3, 3)
plt.plot(x, y3)
plt.subplot(2, 3, 4)
plt.plot(x, y4)
plt.subplot(2, 3, 5)
plt.plot(x, y5)
plt.show()