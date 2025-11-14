from fastapi import FastAPI
import httpx

app = FastAPI()

ALLOWED_USERS = {"6050965589","7268596608","1193564058"}

@app.get("/extract")
async def extract(url: str, user_id: str = None, cptoken: str = None):

    if user_id not in ALLOWED_USERS:
        return {"status": "not_allowed"}

    async with httpx.AsyncClient(timeout=60) as client:

        # CASE 1: url + cptoken → Only Drago API
        if cptoken:
            drago_url = (
                f"https://dragoapi.vercel.app/classplus?"
                f"link={url}&token={cptoken}"
            )

            try:
                res = await client.get(drago_url)
                return {"classplus": res.json()}
            except:
                return {"classplus": "failed"}

        # CASE 2: Only url → Only Covercel API
        else:
            covercel_url = (
                f"https://covercel.vercel.app/extract_keys?"
                f"url={url}@bots_updatee&user_id={user_id}"
            )

            try:
                res = await client.get(covercel_url)
                return {"covercel": res.json()}
            except:
                return {"covercel": "failed"}
