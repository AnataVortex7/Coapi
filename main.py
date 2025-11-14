from fastapi import FastAPI, Request
import requests

app = FastAPI()

@app.get("/extract")
def extract(url: str, user_id: str):
    try:
        # Build target API
        target_api = f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id={user_id}"

        # Call covercel API
        response = requests.get(target_api)

        # Return raw JSON as-it-is
        return response.json()

    except Exception as e:
        return {"error": str(e)}
