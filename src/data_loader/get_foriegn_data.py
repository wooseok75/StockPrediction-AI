import requests
from dotenv import load_dotenv
import os
import get_data
import json
import pandas as pd

APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
BASE_URL = "https://openapi.koreainvestment.com:9443"

if __name__ == "__main__":
    token = get_data.get_access_token()
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-investor"

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": f"{APP_KEY}",
        "appsecret": f"{APP_SECRET}",
        "tr_id": "FHKST01010900",
        "custtype": "P"
    }
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "069500"}

    res = requests.get(url, headers = headers, params = params)
    
    raw_data = res.json()
    
    df = pd.DataFrame(raw_data['output'])
    print(df['frgn_ntby_qty'])