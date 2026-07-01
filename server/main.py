import os
import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, VideoGrants
from pydantic import BaseModel

load_dotenv()

API_KEY = os.environ["LIVEKIT_API_KEY"]
API_SECRET = os.environ["LIVEKIT_API_SECRET"]
LIVEKIT_URL = os.environ["LIVEKIT_URL"]

app = FastAPI(title="QuickBite Token Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    room_name: str | None = None
    participant_identity: str | None = None
    participant_name: str | None = None


@app.post("/token")
def issue_token(req: TokenRequest) -> dict:
    room = req.room_name or "quickbite-support"
    identity = req.participant_identity or "guest"
    name = req.participant_name or identity or "Test user"

    grants = VideoGrants(
        room_join=True,
        room=room,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
    )

    token = (
        AccessToken(API_KEY, API_SECRET)
        .with_identity(identity)
        .with_name(name)
        .with_ttl(datetime.timedelta(hours=1))
        .with_grants(grants)
        .to_jwt()
    )

    print("\n" + "=" * 50)
    print("✅ TOKEN GENERATED SUCCESSFULLY!")
    print("=" * 50)

    return {"server_url": LIVEKIT_URL, "participant_token": token}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
