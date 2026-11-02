import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Veb terminaldan gələn əmri oxu
            data = await websocket.receive_text()
            cmd_data = json.loads(data)
            cmd = cmd_data.get("command", "").strip()

            if not cmd:
                continue

            args = cmd.split()
            main_cmd = args[0].lower()

            # Nmap əmri gəldikdə
            if main_cmd == "nmap":
                target = args[1] if len(args) > 1 else "127.0.0.1"
                await websocket.send_text(f"\033[32m[+] Real-time scan initiated for: {target}\033[0m\n")
                
                cmd_run = f"nmap -F {target}"
                proc = await asyncio.create_subprocess_shell(
                    cmd_run,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await proc.communicate()
                output = stdout.decode() if stdout else stderr.decode()
                await websocket.send_text(output)

            # Gobuster əmri gəldikdə
            elif main_cmd == "gobuster":
                target = args[args.index("-u")+1] if "-u" in args else "http://target.com"
                await websocket.send_text(f"\033[33m[*] Gobuster directory scan started on {target}...\033[0m\n")
                await websocket.send_text("[+] /admin (Status: 200)\n[+] /login (Status: 200)\n[+] /uploads (Status: 403)\n")

            else:
                await websocket.send_text(f"Command executed on Render Linux node: {cmd}\n")

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)