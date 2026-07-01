import os
import time
import datetime

from dotenv import load_dotenv
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import (
    AccessToken,
    CreateAgentDispatchRequest,
    LiveKitAPI,
    VideoGrants,
)
from pydantic import BaseModel

load_dotenv()

API_KEY = os.environ["LIVEKIT_API_KEY"]
API_SECRET = os.environ["LIVEKIT_API_SECRET"]
LIVEKIT_URL = os.environ["LIVEKIT_URL"]

AGENT_NAME = os.getenv("AGENT_NAME", "customer-support-assistant")

app = FastAPI(title="QuickBite Token Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    room_name: Optional[str] = None
    participant_identity: Optional[str] = None
    participant_name: Optional[str] = None


async def dispatch_agent(room_name: str) -> None:
    async with LiveKitAPI() as lk:
        await lk.agent_dispatch.create_dispatch(
            CreateAgentDispatchRequest(agent_name=AGENT_NAME, room=room_name)
        )


@app.post("/api/token", status_code=201)
async def get_token(request: TokenRequest) -> dict:
    try:
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        server_url = os.getenv("LIVEKIT_URL")

        if not all([api_key, api_secret, server_url]):
            raise HTTPException(
                status_code=500,
                detail="Server configuration error",
            )

        room_name = request.room_name or f"room-{int(time.time())}"
        participant_identity = request.participant_identity or f"user-{int(time.time())}"
        participant_name = request.participant_name or "User"

        grants = VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        )

        token = (
            AccessToken(API_KEY, API_SECRET)
            .with_identity(participant_identity)
            .with_name(participant_name)
            .with_ttl(datetime.timedelta(hours=1))
            .with_grants(grants)
        )

        participant_token = token.to_jwt()

        try:
            await dispatch_agent(room_name)
            print(f"[OK] Agent '{AGENT_NAME}' dispatched to room '{room_name}'")
        except Exception as dispatch_err:
            print(f"[WARN] Agent dispatch failed: {dispatch_err}")

        print("\n" + "=" * 50)
        print("[OK] TOKEN GENERATED SUCCESSFULLY!")
        print("=" * 50)

        return {
            "server_url": server_url,
            "participant_token": participant_token,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Token generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate token",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
