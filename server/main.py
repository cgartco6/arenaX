from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from payments import process_payment
from game_engine import start_battle
import os
import uvicorn

app = FastAPI(title="ArenaX API", version="1.0.0")

# Security
API_KEY = os.getenv('API_KEY')
api_key_header = APIKeyHeader(name='X-API-Key')

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "server_time": time.time()}

@app.post("/battle")
async def start_player_battle(player_data: dict, api_key: str = Depends(get_api_key)):
    return start_battle(player_data)

@app.post("/purchase")
async def handle_purchase(payment_data: dict, api_key: str = Depends(get_api_key)):
    try:
        return await process_payment(payment_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
