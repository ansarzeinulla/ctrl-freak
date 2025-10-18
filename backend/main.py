from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json # <-- Добавлен импорт для работы с JSON
import os

# --- Imports from our project ---
from .db import get_db_connection, fetch_record_as_dict # AI import removed

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
    db_conn, db_cursor = None, None # Initialize here to use in finally

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
            
            # --- NEW LOGIC: Fetch from DB and return data ---
            if vacancy_id and resume_id:
                # Establish DB connection for this message
                db_conn, db_cursor = get_db_connection()

                # Fetch records from the database
                vacancy_data = fetch_record_as_dict(db_cursor, "vacancies", vacancy_id)
                resume_data = fetch_record_as_dict(db_cursor, "resumes", resume_id)
                print(f"Fetched vacancy data: {vacancy_data}")
                print(f"Fetched resume data: {resume_data}")
                if vacancy_data and resume_data:
                    # Combine the fetched data into a single object for the response.
                    # We use json.dumps with default=str to handle data types like dates.
                    # ensure_ascii=False is key for sending Cyrillic characters directly.
                    response_message = json.dumps({
                        "vacancy": vacancy_data,
                        "resume": resume_data
                    }, indent=2, default=str, ensure_ascii=False)
                else:
                    response_message = "Could not find the vacancy or resume details in the database." # Keep this error message

                response = {
                    "message": response_message,
                    "finish_conversation": False
                }
                await websocket.send_text(json.dumps(response))
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    except WebSocketDisconnect:
        # Эта секция более корректно отлавливает закрытие вкладки браузера
        print("Клиент отключился.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Ensure the database connection is closed
        if db_cursor:
            db_cursor.close()
        if db_conn:
            db_conn.close()

# Чтобы можно было запустить как обычный скрипт
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)