import os
import asyncio
import json
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            cmd_data = json.loads(data)
            cmd = cmd_data.get("command", "").strip()

            if not cmd:
                continue

            args = cmd.split()
            main_cmd = args[0].lower()

            executable = shutil.which(main_cmd)

            if executable:
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                output = stdout.decode() if stdout else stderr.decode()
                await websocket.send_text(output)
            else:
                await websocket.send_text(f"[!] '{main_cmd}' aləti Linux node-da tapılmadı.\n")

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
