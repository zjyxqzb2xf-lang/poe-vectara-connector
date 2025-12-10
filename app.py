import os
import json
from fastapi import FastAPI, Request
import requests

app = FastAPI()

def get_corpus_ids():
    corpus_env = {}
    for key, value in os.environ.items():
        if key.startswith("CORPUS_"):
            corpus_env[key.replace("CORPUS_", "").lower()] = value
    return corpus_env

def ask_vectara(question, corpus_id):
    customer_id = os.environ.get("VECTARA_CUSTOMER_ID")
    api_key = os.environ.get("VECTARA_API_KEY")

    url = "https://api.vectara.io/v1/query"

    payload = {
        "query": [
            {
                "query": question,
                "num_results": 5,
                "corpus_key": [
                    {
                        "customer_id": customer_id,
                        "corpus_id": int(corpus_id)
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    r = requests.post(url, headers=headers, data=json.dumps(payload))
    data = r.json()

    try:
        return data["responseSet"][0]["response"][0]["text"]
    except:
        return None

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    corpus_map = get_corpus_ids()
    hits = {}

    for name, corpus_id in corpus_map.items():
        answer = ask_vectara(user_message, corpus_id)
        if answer:
            hits[name] = answer

    if not hits:
        return {"text": "Jag hittade tyvärr ingen information i dina områden."}

    final_answer = ""
    for name, text in hits.items():
        final_answer += f"[{name.upper()}]\n{text}\n\n"

    return {"text": final_answer.strip()}
