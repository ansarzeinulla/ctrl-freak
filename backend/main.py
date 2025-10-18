from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json # <-- Добавлен импорт для работы с JSON

app = FastAPI()

# ВАЖНО: для "тяп-ляп" разрешаем все источники (CORS)
# В реальном проекте так делать нельзя!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Простой HTTP GET эндпоинт
@app.get("/api/hello")
def get_hello_message():
    return {"message": "Привет от FastAPI!"}

# Эндпоинт для WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # The frontend will now send a JSON string. We need to parse it.
            received_data = json.loads(data)

            # Extract data from the received JSON
            user_message = received_data.get("message", "")
            vacancy_id = received_data.get("vacancyId")
            resume_id = received_data.get("resumeId")

            # Check if the client sent a command to end the conversation
            if user_message.lower().strip() == "bye":
                response = {
                    "message": "Диалог завершен. Спасибо!",
                    "finish_conversation": True
                }
                await websocket.send_text(json.dumps(response))
                break
            else:
                # For a regular message, prepare a standard response
                # We mirror back the IDs we received
                response = {
                    "message": f"Бэкенд получил: '{user_message}'",
                    "finish_conversation": False,
                    "vacancyId": vacancy_id,
                    "resumeId": resume_id
                }
                await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        # Эта секция более корректно отлавливает закрытие вкладки браузера
        print("Клиент отключился.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    # finally блок здесь не нужен, FastAPI закроет соединение при выходе из функции

# Чтобы можно было запустить как обычный скрипт
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)