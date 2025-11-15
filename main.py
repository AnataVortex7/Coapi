from fastapi import FastAPI
import httpx
from datetime import datetime, timedelta

app = FastAPI()

# Admin password
ADMIN_KEY = "akshay14332"   # हे बदलून तुझं secret password टाक

# User → Expiry date
USER_VALIDITY = {
    "6050965589": "2090-12-10",
    "1193564058": "2090-12-30",
    "7268596608": "2099-12-30"
}

# HEAD-MECHALE साठी विशेष user list (यात ज्या ids try करायच्या आहेत ते add करा)
SPECIAL_USER_LIST = [
    # उदाहरण: "6050965589", "1193564058"
    "7111644516",
    "6251520627",
    "953685850",
    "7385595817",
    "7200020975",
    "8316601859",
    "7547625729"
]
# Covercel साठी main user optional (तू extract call मधून येणारा user_id वापरतोस तर ही ओव्हरराइड नाही करावी)
# MAIN_USER = "6050965589"

def is_user_valid(user_id):
    if user_id not in USER_VALIDITY:
        return False
    expiry = datetime.strptime(USER_VALIDITY[user_id], "%Y-%m-%d")
    return datetime.now() <= expiry


# -----------------------------------------
# ADMIN: Add user + validity
# -----------------------------------------
@app.get("/admin/add_user")
def add_user(admin_key: str, user_id: str, days: int = 30):

    if admin_key != ADMIN_KEY:
        return {"error": "unauthorized"}

    expiry = datetime.now() + timedelta(days=days)
    USER_VALIDITY[user_id] = expiry.strftime("%Y-%m-%d")

    return {"status": "added", "user_id": user_id, "expiry": USER_VALIDITY[user_id]}


# -----------------------------------------
# ADMIN: Renew user validity
# -----------------------------------------
@app.get("/admin/renew")
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
@app.get("/admin/remove_user")
def remove_user(admin_key: str, user_id: str):

    if admin_key != ADMIN_KEY:
        return {"error": "unauthorized"}

    if user_id in USER_VALIDITY:
        del USER_VALIDITY[user_id]
        return {"status": "removed", "user_id": user_id}

    return {"error": "user_not_found"}
    


# -----------------------------------------
@app.get("/admin/users")
def list_users(admin_key: str):
    if admin_key != ADMIN_KEY:
        return {"error": "not_allowed"}

    return {
        "total_users": len(USER_VALIDITY),
        "users": USER_VALIDITY
    }
# -----------------------------------------
@app.get("/admin/add_special_user")
def add_special_user(admin_key: str, user_id: str):
    if admin_key != ADMIN_KEY:
        return {"error": "unauthorized"}

    if user_id not in SPECIAL_USER_LIST:
        SPECIAL_USER_LIST.append(user_id)

    return {"status": "special_user_added", "special_users": SPECIAL_USER_LIST}
 #----------------------------------------
def clean_response(data):
    if not isinstance(data, dict):
        return None

    # mpd extraction (possible names)
    mpd = (
        data.get("url") or
        data.get("URL") or
        data.get("mpd") or
        data.get("MPD") or
        data.get("mpd_url")
    )

    # key extraction (possible names)
    key = (
        data.get("keys") or
        data.get("KEYS") or
        data.get("key")
    )

    if mpd and not key:
        return {"mpd": mpd}
    if mpd and key:
        return {"mpd": mpd, "key": key}

    return None
# MAIN EXTRACT API
# -----------------------------------------
@app.get("/extract")
async def extract(url: str, user_id: str = None, cptoken: str = None):

    # 1) user validity check (USER_VALIDITY वापरून)
    if not is_user_valid(user_id):
        return {"status": "not_allowed"}

    # 50 sec timeout client
    async with httpx.AsyncClient(timeout=50) as client:

        # -----------------------------
        # DRAGO (if cptoken given)
        # -----------------------------
        if cptoken:
            drago_url = f"https://dragoapi.vercel.app/classplus?link={url}&token={cptoken}"
            try:
                res = await client.get(drago_url)
                data = res.json()
                cleaned = clean_response(data)
                if cleaned:
                    return cleaned
                else:
                    return {"error": "Invalid Response"}
            except Exception:
                return {"error": "Invalid Response"}

        # -----------------------------
        # COVERCEL (try only with provided user_id)
        # -----------------------------
        if user_id:
            covercel_url = f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id={user_id}"
            try:
                res = await client.get(covercel_url)
                data = res.json()
                cleaned = clean_response(data)
                if cleaned:
                    return cleaned
            except Exception:
                # timeout / error → continue to head-mechale
                pass

        # -----------------------------
        # HEAD-MECHALE (try SPECIAL_USER_LIST)
        # -----------------------------
        for sp_user in SPECIAL_USER_LIST:
            head_url = (
                "https://head-micheline-botupdatevip-f1804c58.koyeb.app/get_keys"
                f"?url={url}@botupdatevip4u&user_id={sp_user}"
            )

            try:
                res2 = await client.get(head_url)
                hdata = res2.json()
                cleaned = clean_response(hdata)
                if cleaned:
                    return cleaned
            except Exception:
                # try next special user
                continue

        # -----------------------------
        # All attempts failed
        # -----------------------------
        return {"error": "Main Server Issue"}
