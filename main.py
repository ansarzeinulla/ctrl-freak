# main.py
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
            
            # --- НАЧАЛО ИЗМЕНЕНИЙ ---

            # Проверяем, прислал ли клиент команду для завершения
            if data.lower().strip() == "bye":
                # Если да, готовим ответ с флагом finish_conversation: True
                response = {
                    "message": "Диалог завершен. Спасибо!",
                    "finish_conversation": True
                }
                # Отправляем JSON-строку
                await websocket.send_text(json.dumps(response))
                # Выходим из цикла, что приведет к закрытию соединения
                break 
            
            # Если это обычное сообщение
            else:
                # Готовим стандартный ответ с флагом finish_conversation: False
                response = {
                    "message": f"Бэкенд получил: '{data}'",
                    "finish_conversation": False
                }
                # Отправляем JSON-строку
                await websocket.send_text(json.dumps(response))

            # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    except WebSocketDisconnect:
        # Эта секция более корректно отлавливает закрытие вкладки браузера
        print("Клиент отключился.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    # finally блок здесь не нужен, FastAPI закроет соединение при выходе из функции

# Чтобы можно было запустить как обычный скрипт
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)