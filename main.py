from fastapi import FastAPI
import requests

app = FastAPI()

# Allowed users list
ALLOWED_USERS = {"6050965589"}   # इथे फक्त access हव्या असलेल्या लोकांचे user_id टाक

@app.get("/extract")
def extract(url: str, user_id: str = None, cptoken: str = None):

    # ❌ Not allowed
    if user_id not in ALLOWED_USERS:
        return {"status": "not_allowed"}

    result = {}

    # 1) Covercel API call
    covercel_url = f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id={user_id}"
    try:
        r1 = requests.get(covercel_url)
        result["covercel"] = r1.json()
    except:
        result["covercel"] = {"error": "covercel_api_failed"}

    # 2) Drago ClassPlus API call (optional)
    if cptoken:
        drago_url = f"https://dragoapi.vercel.app/classplus?link={url}&token={cptoken}"
        try:
            r2 = requests.get(drago_url)
            result["classplus"] = r2.json()
        except:
            result["classplus"] = {"error": "classplus_api_failed"}

    return result
