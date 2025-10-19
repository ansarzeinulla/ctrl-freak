from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os

# --- Imports from our project ---
# Make sure to import the new function
from db import get_db_connection, fetch_record_as_dict, insert_or_update_result
from ai import generate_ai_response

app = FastAPI()

# --- CORS Configuration ---
# Мы явно указываем, с каких адресов можно делать запросы к нашему API.
# Это гораздо безопаснее, чем разрешать всем ("*").
origins = [
    "http://localhost:8080",  # Адрес, на котором работает фронтенд-виджет
    "http://127.0.0.1:8080", # Иногда браузеры используют этот адрес вместо localhost
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Разрешает отправку cookies и заголовков авторизации
    allow_methods=["GET", "POST", "OPTIONS"],  # Явно разрешаем только нужные методы
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
    ],  # Явно разрешаем заголовки
)

# Simple HTTP GET endpoint
@app.get("/api/hello")
def get_hello_message():
    return {"message": "Hello from FastAPI!"}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    db_conn, db_cursor = None, None
    conversation_history = []
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        error_response = {
            "message": "Server configuration error: AI service is unavailable.",
            "finish_conversation": True
        }
        await websocket.send_text(json.dumps(error_response))
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            try:
                incoming_data = json.loads(data)
                user_message = incoming_data.get("text", "")
                vacancy_id = incoming_data.get("vacancy_id")
                resume_id = incoming_data.get("resume_id")
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"message": "Invalid data format.", "finish_conversation": True}))
                break

            if not vacancy_id or not resume_id:
                await websocket.send_text(json.dumps({"message": "Vacancy or Resume ID is missing.", "finish_conversation": True}))
                break

            if user_message and user_message.lower() != "start":
                conversation_history.append(f"Candidate: {user_message}")

            try:
                db_conn, db_cursor = get_db_connection()
                vacancy_data = fetch_record_as_dict(db_cursor, "vacancies", vacancy_id)
                resume_data = fetch_record_as_dict(db_cursor, "resumes", resume_id)

                if not vacancy_data or not resume_data:
                    await websocket.send_text(json.dumps({"message": "Could not find vacancy or resume details.", "finish_conversation": True}))
                    break

                vacancy_str = json.dumps(vacancy_data, default=str, indent=2)
                resume_str = json.dumps(resume_data, default=str, indent=2)
                history_str = "\n".join(conversation_history)

                ai_response_text = generate_ai_response(api_key, vacancy_str, resume_str, history_str)

                try:
                    final_analysis = json.loads(ai_response_text)
                    if "final_score" in final_analysis and "summary" in final_analysis:
                        score = final_analysis["final_score"]
                        summary = final_analysis["summary"]
                        print(f"--- FINAL ANALYSIS COMPLETE ---")
                        print(f"Candidate Suitability Score: {score}%")
                        print(f"Summary: {summary}")

                        # --- NEW: Save the result to the database ---
                        update_conn, update_cursor = None, None
                        try:
                            update_conn, update_cursor = get_db_connection()
                            # Store the entire JSON analysis as the output
                            output_to_save = json.dumps(final_analysis)
                            insert_or_update_result(update_cursor, vacancy_id, resume_id, output_to_save)
                            print("Successfully saved final analysis to the database.")
                        except Exception as e:
                            print(f"Failed to save result to database: {e}")
                        finally:
                            if update_cursor: update_cursor.close()
                            if update_conn: update_conn.close()
                        # --- END NEW ---

                        final_message = f"Analysis complete. Candidate suitability: {score}%. {summary}"
                        response = {"message": final_message, "finish_conversation": True}
                        await websocket.send_text(json.dumps(response))
                        break

                    else:
                        raise json.JSONDecodeError("Not final analysis format", ai_response_text, 0)
                except json.JSONDecodeError:
                    bot_question = ai_response_text.strip()
                    conversation_history.append(f"AI Assistant: {bot_question}")
                    response = {"message": bot_question, "finish_conversation": False}
                    await websocket.send_text(json.dumps(response))

            finally:
                if db_cursor:
                    db_cursor.close()
                if db_conn:
                    db_conn.close()

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred in the WebSocket: {e}")
    finally:
        if db_cursor:
            db_cursor.close()
        if db_conn:
            db_conn.close()
        print("WebSocket connection closed.")

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY environment variable not set. AI features will fail.")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)