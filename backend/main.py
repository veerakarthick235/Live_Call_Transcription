import asyncio
import base64
import json
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse # NEW: Added FileResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
import websockets

# Load API key from .env file
load_dotenv()

app = FastAPI()

# --- Connection Manager for Frontend ---
# This class manages the WebSocket connection to the browser to display the text.
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_text(self, text: str):
        for connection in self.active_connections:
            await connection.send_text(text)

manager = ConnectionManager()

# --- Twilio TwiML Endpoint ---
# This endpoint generates instructions for Twilio when a call is received.
@app.post("/twilio")
async def handle_twilio_call(request: Request):
    response = VoiceResponse()
    connect = Connect()

    # The <Stream> verb tells Twilio to start streaming the call audio
    # to our backend's WebSocket endpoint (/ws).
    # NOTE: ngrok free plan uses a different URL for wss, so we replace http with ws
    hostname = request.url.hostname
    connect.append(Stream(url=f"wss://{hostname}/ws"))
    
    response.append(connect)
    response.say("Transcription has started.")
    
    return HTMLResponse(content=str(response), media_type="application/xml")

# --- Frontend WebSocket Endpoint ---
# The browser connects here to receive live transcripts.
@app.websocket("/ws-frontend")
async def websocket_frontend_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Twilio Audio Stream WebSocket Endpoint ---
# Twilio connects here to stream the call audio.
@app.websocket("/ws")
async def websocket_audio_endpoint(twilio_ws: WebSocket):
    await twilio_ws.accept()
    ASSEMBLYAI_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=8000"

    try:
        # Connect to AssemblyAI's real-time transcription WebSocket
        async with websockets.connect(
            ASSEMBLYAI_URL,
            extra_headers={"Authorization": os.getenv("ASSEMBLYAI_API_KEY")}
        ) as assemblyai_ws:
            print("Connected to Twilio and AssemblyAI.")

            # Define two asynchronous tasks:
            # 1. Forwarding audio from Twilio to AssemblyAI
            # 2. Receiving transcripts from AssemblyAI and broadcasting to the frontend
            
            async def forward_audio():
                while True:
                    message_str = await twilio_ws.receive_text()
                    message_json = json.loads(message_str)

                    if message_json.get('event') == 'media':
                        media_payload = message_json['media']['payload']
                        # AssemblyAI requires the audio data to be base64 encoded
                        await assemblyai_ws.send(json.dumps({"audio_data": media_payload}))
                    elif message_json.get('event') == 'stop':
                        break

            async def receive_transcripts():
                while True:
                    response_json = await assemblyai_ws.recv()
                    transcript = json.loads(response_json)
                    if transcript.get('message_type') == 'FinalTranscript' and transcript.get('text'):
                        # When a final transcript is received, broadcast it to the frontend.
                        await manager.broadcast_text(transcript['text'])

            # Run both tasks concurrently
            await asyncio.gather(forward_audio(), receive_transcripts())

    except WebSocketDisconnect:
        print("Twilio WebSocket disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")

# NEW: Add this function to serve the frontend
@app.get("/")
async def get_frontend():
    """Serves the frontend HTML file."""
    return FileResponse('../frontend/index.html')