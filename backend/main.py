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
            try:
                # Парсим входящие данные как JSON
                incoming_data = json.loads(data)
                message_text = incoming_data.get("text", "")
                vacancy_id = incoming_data.get("vacancy_id") # Получаем ID вакансии
                resume_id = incoming_data.get("resume_id")   # Получаем ID резюме
            except json.JSONDecodeError:
                # Если пришел не JSON, обрабатываем как обычный текст для обратной совместимости
                message_text = data
                vacancy_id = None
                resume_id = None

            # Проверяем, прислал ли клиент команду для завершения
            if message_text.lower().strip() == "bye":
                response = {
                    "message": "Диалог завершен. Спасибо!",
                    "finish_conversation": True
                }
                await websocket.send_text(json.dumps(response))
                break 
            
            # Если это обычное сообщение
            else:
                # Формируем ответ, включая полученный vacancy_id
                response = {
                    "message": f"Бэкенд получил: '{message_text}' для вакансии ID: {vacancy_id} и резюме ID: {resume_id}",
                    "finish_conversation": False
                }
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)