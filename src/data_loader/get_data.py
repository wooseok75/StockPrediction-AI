from dotenv import load_dotenv
import os
import requests
import json
import time
import pandas as pd

load_dotenv()

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
BASE_URL = "https://openapi.koreainvestment.com:9443"

# BULL장 데이터셋
# START_DATE = "20250527"
# END_DATE = "20260527"
# OUTPUT_FILENAME = "bull_1year_data.csv"

# BEAR장 데이터셋
START_DATE = "20220101"
END_DATE = "20221231"
OUTPUT_FILENAME = "bear_1year_data.csv"

# 토큰 발급 함수
def get_access_token():
    token_file = "token.txt"
    # 기존 토큰 들고오기
    if os.path.exists(token_file):
        file_age = time.time() - os.path.getmtime(token_file)
        if (file_age < 12 * 3600):
            with open(token_file, 'r') as f:
                token = f.read().strip()
            if token:
                return token

    # 신규 토큰 발급받기
    url = f"{BASE_URL}/oauth2/tokenP"
    headers = {"content-type": "application/json; charset=UTF-8"}
    bodys = {
        "grant_type": "client_credentials",
        "appkey": f"{APP_KEY}",
        "appsecret": f"{APP_SECRET}"
    }

    res = requests.post(url, headers = headers, data = json.dumps(bodys))
    if res.status_code == 200:
        token = res.json()['access_token']
        with open(token_file, 'w') as f:
            f.write(token)
        return token
    else:
        return None
    
# 1분봉 DataFrame 저장 함수
def get_1min_df(token, target_date):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": f"{APP_KEY}",
        "appsecret": f"{APP_SECRET}",
        "tr_id": "FHKST03010230",
        "custtype": "P"
        }
    
    all_dfs = []
    current_time = "153000"

    while True:
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "069500",
            "FID_INPUT_HOUR_1": f"{current_time}",
            "FID_INPUT_DATE_1": f"{target_date}",
            "FID_PW_DATA_INCU_YN": "N",
            "FID_FAKE_TICK_INCU_YN": "N"
        }
        res = requests.get(url, headers = headers, params = params)

        if res.status_code != 200:
            print(f"통신 불량 원인: {res.status_code}")
            break
        raw_data = res.json()
        if 'output2' not in raw_data or raw_data['output2'] is None:
            print("다른 것 수신받음")
            break

        df = pd.DataFrame(raw_data['output2'])
        all_dfs.append(df)

        earlist_time = df.iloc[-1]['stck_cntg_hour']

        if int(earlist_time) <= 90000: break

        if current_time == earlist_time: 
            break
        
        current_time = earlist_time

        time.sleep(0.2)

    # DataFrame 예쁘게 가공하기
    full_df = pd.concat(all_dfs)
    full_df = full_df.drop_duplicates(subset = ['stck_bsop_date', 'stck_cntg_hour'], keep = 'first')
    full_df = full_df.drop(columns = ['acml_tr_pbmn'])
    full_df.columns = ['Date', 'Time', 'Close', 'Open', 'High', 'Low', 'Volume']
    full_df = full_df[::-1].reset_index(drop = True)
    full_df = full_df[full_df['Time']!='153000']
    full_df[['Close', 'Open', 'High', 'Low', 'Volume']] = full_df[['Close', 'Open', 'High', 'Low', 'Volume']].apply(pd.to_numeric)
    return full_df

# 1분봉 -> 5분봉 변환 함수
def convert_to_5min(df):
    df['DateTime'] = pd.to_datetime(df['Date'] + df['Time'].astype(str).str.zfill(6), format = '%Y%m%d%H%M%S')
    df.set_index('DateTime', inplace = True)

    df_5min = df.resample('5min', closed='right', label='right').agg({ # 09:00:00~09:04:00 -> 09:01:00~09:05:00으로 변경
        'Close': 'last',
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Volume': 'sum'
    }).dropna()
    df_5min.reset_index(inplace = True)
    return df_5min

if __name__ == '__main__':
    token = get_access_token()
    
    date_list = pd.date_range(start = START_DATE, end = END_DATE, freq = 'B').strftime("%Y%m%d").tolist()
    
    full_df = []

    for target_date in date_list:
        try:
            df_1min = get_1min_df(token, target_date)

            if df_1min is None or df_1min.empty:
                print(f"{target_date}의 값이 없으므로 넘어갑니다.")
                continue
            actual_date = df_1min['Date'].iloc[0]

            if actual_date != target_date:
                print(f"{target_date}는 공휴일이므로 넘어갑니다.")
                continue

            df_5min = convert_to_5min(df_1min)

            if df_5min is not None and not df_5min.empty:
                full_df.append(df_5min)
                print(f"{target_date} 일일 데이터 저장 완료!")

        except Exception as e:
            print(f"{target_date} 오류 발생 -> {e}")
        
        time.sleep(1.0)
    
    if full_df:
        master_df = pd.concat(full_df, ignore_index = True)
        
        current_dir = os.path.dirname(os.path.abspath(__file__)) # ../data_loader
        root_dir = os.path.dirname(os.path.dirname(current_dir)) # C:/StockPrediction-AI
        save_dir = os.path.join(root_dir, "data")
        os.makedirs(save_dir, exist_ok = True)

        file_path = os.path.join(save_dir, OUTPUT_FILENAME)
        master_df.to_csv(file_path, index = False, encoding = 'UTF-8')
        print("\n1년치 데이터를 저장하였습니다!")