from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json # <-- Добавлен импорт для работы с JSON
import os

# --- Imports from our project ---
from .db import get_db_connection, fetch_record_as_dict
from .ai import generate_ai_response

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
    db_conn, db_cursor = None, None
    conversation_history = []
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Handle missing API key gracefully
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
                # Handle malformed JSON or non-JSON messages
                await websocket.send_text(json.dumps({"message": "Invalid data format.", "finish_conversation": True}))
                break

            if not vacancy_id or not resume_id:
                await websocket.send_text(json.dumps({"message": "Vacancy or Resume ID is missing.", "finish_conversation": True}))
                break

            # Append user's message to history (if it's not the initial trigger)
            if user_message and user_message != "start":
                conversation_history.append(f"Candidate: {user_message}")

            try:
                db_conn, db_cursor = get_db_connection()
                vacancy_data = fetch_record_as_dict(db_cursor, "vacancies", vacancy_id)
                resume_data = fetch_record_as_dict(db_cursor, "resumes", resume_id)

                if not vacancy_data or not resume_data:
                    await websocket.send_text(json.dumps({"message": "Could not find vacancy or resume details.", "finish_conversation": True}))
                    break

                # Convert DB records to string for the AI prompt
                vacancy_str = json.dumps(vacancy_data, default=str, indent=2)
                resume_str = json.dumps(resume_data, default=str, indent=2)
                history_str = "\n".join(conversation_history)

                # Call the AI service
                ai_response_text = generate_ai_response(api_key, vacancy_str, resume_str, history_str)

                # Check if the AI response is a final score in JSON format
                try:
                    final_analysis = json.loads(ai_response_text)
                    if "final_score" in final_analysis and "summary" in final_analysis:
                        score = final_analysis["final_score"]
                        summary = final_analysis["summary"]
                        print(f"--- FINAL ANALYSIS COMPLETE ---")
                        print(f"Candidate Suitability Score: {score}%")
                        print(f"Summary: {summary}")

                        # Send final message and close conversation
                        final_message = f"Analysis complete. Candidate suitability: {score}%. {summary}"
                        response = {"message": final_message, "finish_conversation": True}
                        await websocket.send_text(json.dumps(response))
                        break # Exit the while loop
                    else:
                        # It's JSON but not the format we want, treat as a regular question
                        raise json.JSONDecodeError("Not final analysis format", ai_response_text, 0)
                except json.JSONDecodeError:
                    # AI returned a question, not a final score
                    bot_question = ai_response_text.strip()
                    conversation_history.append(f"AI Assistant: {bot_question}")
                    response = {"message": bot_question, "finish_conversation": False}
                    await websocket.send_text(json.dumps(response))

            finally:
                # Close DB connection for this message cycle
                if db_cursor:
                    db_cursor.close()
                if db_conn:
                    db_conn.close()

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred in the WebSocket: {e}")
    finally:
        # Final cleanup if connection was left open due to an error
        if db_cursor:
            db_cursor.close()
        if db_conn:
            db_conn.close()
        print("WebSocket connection closed.")

# Чтобы можно было запустить как обычный скрипт
if __name__ == "__main__":
    # Ensure the API key is available on startup
    if not os.environ.get("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY environment variable not set. AI features will fail.")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)