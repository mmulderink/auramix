"""
WebSocket server for Rat Assistant.
Streams assistant responses and rendered animation frames to the frontend app.
"""

import asyncio
import base64
import os
from io import BytesIO
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from PIL import Image, ImageDraw

from llm.orchestrator import AgentOrchestrator

app = FastAPI()

orchestrator = AgentOrchestrator()
clients: Set[WebSocket] = set()

FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "520"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "360"))
FRAME_FPS = float(os.getenv("FRAME_FPS", "12"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "status", "message": "connected"})
    clients.add(ws)

    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") != "user_text":
                continue

            text = (data.get("text") or "").strip()
            if not text:
                continue

            await ws.send_json({"type": "status", "message": "processing"})
            result = await asyncio.to_thread(orchestrator.process_user_input, text)

            payload = {
                "type": "assistant",
                "message": result.get("message"),
                "emotion": result.get("emotion"),
                "intensity": result.get("intensity"),
                "animation": result.get("animation")
            }
            await ws.send_json(payload)
    except WebSocketDisconnect:
        clients.discard(ws)
        return
    except Exception as exc:
        await ws.send_json({"type": "error", "message": str(exc)})
    finally:
        clients.discard(ws)


@app.on_event("startup")
async def start_frame_stream():
    asyncio.create_task(_frame_broadcaster())


async def _frame_broadcaster():
    frame_gen = orchestrator.start_frame_stream(
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        fps=int(FRAME_FPS)
    )

    while True:
        if not clients:
            await asyncio.sleep(0.2)
            continue

        frame = next(frame_gen)
        png_bytes = _render_frame_png(frame, FRAME_WIDTH, FRAME_HEIGHT)
        encoded = base64.b64encode(png_bytes).decode("ascii")

        payload = {
            "type": "frame",
            "format": "png",
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
            "data": encoded
        }

        dead = []
        for ws in clients:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)

        for ws in dead:
            clients.discard(ws)

        await asyncio.sleep(1.0 / FRAME_FPS)


def _render_frame_png(frame, width: int, height: int) -> bytes:
    image = Image.new("RGB", (width, height), (27, 26, 31))
    draw = ImageDraw.Draw(image)

    if frame.projected_vertices is None or frame.faces is None:
        return _encode_image(image)

    vertices = frame.projected_vertices
    faces = frame.faces
    colors = frame.face_colors or [(155, 107, 60)] * len(faces)
    transformed = frame.transformed_vertices

    order = list(range(len(faces)))
    if transformed is not None:
        depths = []
        for idx, face in enumerate(faces):
            z = (transformed[face[0]][2] + transformed[face[1]][2] + transformed[face[2]][2]) / 3.0
            depths.append((z, idx))
        order = [idx for _, idx in sorted(depths, key=lambda item: item[0])]

    for idx in order:
        face = faces[idx]
        if any(v >= len(vertices) for v in face):
            continue

        points = [
            (float(vertices[face[0]][0]), float(vertices[face[0]][1])),
            (float(vertices[face[1]][0]), float(vertices[face[1]][1])),
            (float(vertices[face[2]][0]), float(vertices[face[2]][1]))
        ]

        color = colors[idx]
        if isinstance(color, tuple) and len(color) == 3:
            fill = tuple(int(max(0, min(1, c)) * 255) for c in color)
        else:
            fill = (155, 107, 60)

        draw.polygon(points, fill=fill)

    return _encode_image(image)


def _encode_image(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()
