import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

# Başlangıç dizini olarak uygulamanın çalıştığı yeri alıyoruz
current_dir = os.getcwd()

# Sistemde araçların arandığı standart PATH yollarını garantiliyoruz
custom_env = {
    **os.environ,
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:" + os.environ.get("PATH", "")
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global current_dir
    await websocket.accept()
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            
            try:
                cmd_data = json.loads(raw_data)
                cmd = cmd_data.get("command", "").strip()
            except Exception:
                cmd = raw_data.strip()

            if not cmd:
                continue

            # 'cd' komutlarını gerçek dizin mantığı ile yönetiyoruz
            if cmd.startswith("cd ") or cmd == "cd":
                new_dir = cmd[3:].strip() if len(cmd) > 2 else os.path.expanduser("~")
                target_dir = os.path.abspath(os.path.join(current_dir, new_dir))
                
                if os.path.exists(target_dir) and os.path.isdir(target_dir):
                    current_dir = target_dir
                    # Ön yüze güncel dizini bildiriyoruz
                    await websocket.send_text(json.dumps({
                        "type": "cwd",
                        "pwd": current_dir,
                        "output": ""
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "output",
                        "output": f"bash: cd: {new_dir}: No such file or directory\n"
                    }))
                continue

            # Komutu sistem ortam değişkenleri (PATH) ile çalıştırıyoruz
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=current_dir,
                env=custom_env
            )
            
            stdout, stderr = await proc.communicate()
            output = stdout.decode('utf-8', errors='ignore') if stdout else stderr.decode('utf-8', errors='ignore')
            
            if not output.strip():
                output = "\n"

            await websocket.send_text(json.dumps({
                "type": "output",
                "output": output
            }))

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
