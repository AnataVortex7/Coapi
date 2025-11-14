from fastapi import FastAPI
import httpx
from datetime import datetime, timedelta

app = FastAPI()

# Admin password
ADMIN_KEY = "Akshay@1181"   # हे बदलून तुझं secret password टाक

# User → Expiry date
USER_VALIDITY = {
    "6050965589": "2090-12-10",
    "1193564058": "2090-12-30",
    "7268596608": "2099-12-30"
}


def is_user_valid(user_id):
    if user_id not in USER_VALIDITY:
        return False
    expiry = datetime.strptime(USER_VALIDITY[user_id], "%Y-%m-%d")
    return datetime.now() <= expiry


# -----------------------------------------
# ADMIN: Add user + validity
# -----------------------------------------
@app.post("/admin/add_user")
def add_user(admin_key: str, user_id: str, days: int = 30):

    if admin_key != ADMIN_KEY:
        return {"error": "unauthorized"}

    expiry = datetime.now() + timedelta(days=days)
    USER_VALIDITY[user_id] = expiry.strftime("%Y-%m-%d")

    return {"status": "added", "user_id": user_id, "expiry": USER_VALIDITY[user_id]}


# -----------------------------------------
# ADMIN: Renew user validity
# -----------------------------------------
@app.post("/admin/renew")
def renew_user(admin_key: str, user_id: str, days: int = 30):

    if admin_key != ADMIN_KEY:
        return {"error": "unauthorized"}

    if user_id not in USER_VALIDITY:
        return {"error": "user_not_found"}

    new_expiry = datetime.now() + timedelta(days=days)
    USER_VALIDITY[user_id] = new_expiry.strftime("%Y-%m-%d")

    return {"status": "renewed", "new_expiry": USER_VALIDITY[user_id]}


# -----------------------------------------

@app.get("/")
def home():
    return {"status": "running", "message": "API is live!"}
    
# ADMIN: Remove user
# -----------------------------------------
@app.post("/admin/remove_user")
def remove_user(admin_key: str, user_id: str):

    if admin_key != ADMIN_KEY:
        return {"error": "unauthorized"}

    if user_id in USER_VALIDITY:
        del USER_VALIDITY[user_id]
        return {"status": "removed", "user_id": user_id}

    return {"error": "user_not_found"}
    


# -----------------------------------------
# MAIN EXTRACT API
# -----------------------------------------
@app.get("/extract")
async def extract(url: str, user_id: str = None, cptoken: str = None):

    if not is_user_valid(user_id):
        return {"status": "not_allowed"}

    async with httpx.AsyncClient(timeout=60) as client:

        # CASE 1: Drago (url + token)
        if cptoken:
            drago_url = f"https://dragoapi.vercel.app/classplus?link={url}&token={cptoken}"
            try:
                res = await client.get(drago_url)
                return {"classplus": res.json()}
            except:
                return {"classplus": "failed"}

        # CASE 2: Covercel (only url)
        else:
            covercel_url = f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id={user_id}"
            try:
                res = await client.get(covercel_url)
                return {"classplus co": res.json()}
            except:
                return {"classplus co": "failed"}
