from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()

# Allowed user IDs
ALLOWED_USERS = {"6050965589"}


@app.get("/extract")
async def extract(url: str, user_id: str = None, cptoken: str = None):

    # ❌ Block unauthorized users
    if user_id not in ALLOWED_USERS:
        return {"status": "not_allowed"}

    async with httpx.AsyncClient(timeout=60) as client:

        # ----------- Prepare URLs -----------
        covercel_url = (
            f"https://covercel.vercel.app/extract_keys?"
            f"url={url}@bots_updatee&user_id={user_id}"
        )

        tasks = [client.get(covercel_url)]  # Covercel always first

        if cptoken:
            drago_url = (
                f"https://dragoapi.vercel.app/classplus?"
                f"link={url}&token={cptoken}"
            )
            tasks.append(client.get(drago_url))

        # ------------ Run all requests concurrently -------------
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    # ------------ Build final JSON response -------------
    result = {}

    # Covercel response
    try:
        result["covercel"] = responses[0].json()
    except:
        result["covercel"] = {"error": "covercel_failed"}

    # Drago response (if requested)
    if cptoken:
        try:
            result["classplus"] = responses[1].json()
        except:
            result["classplus"] = {"error": "classplus_failed"}

    return result
