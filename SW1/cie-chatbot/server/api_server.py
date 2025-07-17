##pip install fastapi uvicorn kafka-python aioredis python-dotenv
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kafka import KafkaProducer
from redis import asyncio as aioredis
import json
import uuid
import time
from typing import Dict
import uvicorn

app = FastAPI()

# CORS Configuration (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
WEBSOCKET_TIMEOUT = float(os.getenv("WEBSOCKET_TIMEOUT", "300"))  # 5 minutes

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',
    retries=5,
    retry_backoff_ms=1000,
    max_in_flight_requests_per_connection=1
)

# Initialize Redis
redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

class AskRequest(BaseModel):
    session_id: str
    correlation_id: str
    question: str

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.redis_pubsub = None

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_json(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(data)
            except WebSocketDisconnect:
                self.disconnect(session_id)

manager = ConnectionManager()

@app.post("/ask")
async def ask_question(request: AskRequest):
    """Endpoint for submitting questions to Kafka"""
    # Store initial state in Redis
    await redis.setex(
        f"response:{request.session_id}:{request.correlation_id}", 
        WEBSOCKET_TIMEOUT,
        json.dumps({
            "status": "received",
            "progress": 0,
            "timestamp": time.time()
        })
    )
    
    # Create Kafka message
    message = {
        "metadata": {
            "correlation_id": request.correlation_id,
            "session_id": request.session_id,
            "timestamp": time.time()
        },
        "payload": {
            "question": request.question,
            "language": "en"  # Can detect language here
        }
    }
    
    # Send to Kafka (async)
    producer.send("questions-raw", value=message)
    
    return {"status": "accepted", "correlation_id": request.correlation_id}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    print("Inside Websocket call to process the Session ID")
    try:
        while True:
            # Keep connection alive (client can send ping)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)

@app.get("/responses/{session_id}/{correlation_id}")
async def get_response(session_id: str, correlation_id: str):
    """Fallback endpoint for HTTP polling"""
    response = await redis.get(f"response:{session_id}:{correlation_id}")
    if not response:
        raise HTTPException(status_code=404, detail="Response not found or expired")
    return json.loads(response)

# === Core Processing Functions ===
async def process_kafka_message(message: dict):
    """This would be in your separate processing service"""
    session_id = message["metadata"]["session_id"]
    correlation_id = message["metadata"]["correlation_id"]
    
    # 1. Update progress (example)
    await update_progress(session_id, correlation_id, 25)
    
    # 2. Process question (your RAG logic here)
    # ...
    
    # 3. Send final response
    await dispatch_response(
        session_id=session_id,
        correlation_id=correlation_id,
        response="This is the generated answer from your RAG system",
        status="completed"
    )

async def update_progress(session_id: str, correlation_id: str, progress: int):
    """Update progress through both WebSocket and Redis"""
    update_msg = {
        "correlation_id": correlation_id,
        "progress": progress,
        "status": "processing",
        "timestamp": time.time()
    }
    
    # 1. Update Redis
    await redis.setex(
        f"response:{session_id}:{correlation_id}", 
        WEBSOCKET_TIMEOUT,
        json.dumps(update_msg)
    )
    
    # 2. Push via WebSocket if connected
    await manager.send_json(session_id, update_msg)

async def dispatch_response(session_id: str, correlation_id: str, response: str, status: str):
    """Final response dispatcher"""
    final_msg = {
        "correlation_id": correlation_id,
        "response": response,
        "status": status,
        "timestamp": time.time()
    }
    
    # 1. Update Redis
    await redis.setex(
        f"response:{session_id}:{correlation_id}", 
        WEBSOCKET_TIMEOUT,
        json.dumps(final_msg)
    )
    
    # 2. Push via WebSocket
    await manager.send_json(session_id, final_msg)
    
    # 3. Optionally publish to Kafka
    producer.send("responses-completed", value=final_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)