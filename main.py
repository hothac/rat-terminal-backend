import os
import asyncio
import json
import pty
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # PTY boyutlarını tanımlıyoruz
    master, slave = pty.openpty()
    
    # bash kabuğunu --noediting ve tty modunda başlatıyoruz
    proc = await asyncio.create_subprocess_exec(
        '/bin/bash', '--login',
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True,
        env={**os.environ, "TERM": "xterm-256color", "PS1": "\\u@cyber-hub:\\w$ "}
    )
    os.close(slave)

    async def read_stdout():
        while True:
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, os.read, master, 1024)
                if not data:
                    break
                await websocket.send_text(data.decode('utf-8', errors='ignore'))
            except Exception:
                break

    read_task = asyncio.create_task(read_stdout())

    try:
        while True:
            raw_data = await websocket.receive_text()
            cmd_data = json.loads(raw_data)
            cmd = cmd_data.get("command", "").strip()

            if cmd:
                os.write(master, (cmd + "\n").encode('utf-8'))

    except WebSocketDisconnect:
        proc.terminate()
        read_task.cancel()
        os.close(master)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
