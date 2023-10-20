from fastapi import FastAPI, WebSocket

app = FastAPI()

# Список подключенных клиентов
connected_clients = []



@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await send_message_to_all(message)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        connected_clients.remove(websocket)


async def send_message_to_all(message: str):
    for client in connected_clients:
        await client.send_text(message)
