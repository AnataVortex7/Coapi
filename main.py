from fastapi import FastAPI
import httpx

app = FastAPI()

# Allowed users
ALLOWED_USERS = {"6050965589"}

@app.get("/extract")
async def extract(url: str, user_id: str = None, cptoken: str = None):

    # Block unwanted users
    if user_id not in ALLOWED_USERS:
        return {"status": "not_allowed"}

    async with httpx.AsyncClient(timeout=60) as client:
        tasks = []

        # Covercel API
        covercel_url = (
            f"https://covercel.vercel.app/extract_keys?"
            f"url={url}@bots_updatee&user_id={user_id}"
        )
        tasks.append(client.get(covercel_url))

        # Drago API
        if cptoken:
            drago_url = (
                f"https://dragoapi.vercel.app/classplus?"
                f"link={url}&token={cptoken}"
            )
            tasks.append(client.get(drago_url))

        # Run tasks concurrently (parallel)
        responses = await httpx.AsyncClient.gather(*tasks)

    # Build response dynamically
    result = {}

    if len(responses) >= 1:
        result["Akshay"] = responses[0].json()

    if len(responses) == 2:
        result["Akshay1"] = responses[1].json()

    return result
