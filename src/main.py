from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv

from services.google_sheets_service import GoogleSheetsService
from services.ai_agent import AIAgent
from config.settings import settings

load_dotenv()

app = FastAPI(
    title="TableAgent API", 
    version="1.0.0",
    description="ИИ-агент для работы с инструментами realtycalendar.ru"
)

# Инициализация сервисов
sheets_service = GoogleSheetsService()
ai_agent = AIAgent()

class QuestionRequest(BaseModel):
    question: str
    sheet_id: str = None

class ToolInfo(BaseModel):
    name: str
    url: str
    description: str = None

@app.get("/")
def read_root():
    return {
        "message": "TableAgent API is running",
        "version": "1.0.0",
        "model": settings.model_config.model_name
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": settings.model_config.model_name,
        "api_configured": bool(settings.OPENAI_API_KEY)
    }

@app.get("/tools/{sheet_id}")
def get_all_tools(sheet_id: str):
    """Получить все инструменты из таблицы"""
    try:
        tools = sheets_service.get_tools_data(sheet_id)
        return {
            "tools": tools,
            "count": len(tools),
            "sheet_id": sheet_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def ask_question(request: QuestionRequest):
    """Задать вопрос агенту"""
    try:
        # Используем ID таблицы из запроса или из настроек
        sheet_id = request.sheet_id or settings.SAMPLE_SPREADSHEET_ID
        
        if not sheet_id:
            raise HTTPException(
                status_code=400, 
                detail="Не указан ID таблицы. Укажите sheet_id в запросе или настройте SAMPLE_SPREADSHEET_ID в .env"
            )
        
        # Получаем все инструменты
        tools = sheets_service.get_tools_data(sheet_id)
        
        if not tools:
            raise HTTPException(
                status_code=404,
                detail="Инструменты не найдены в указанной таблице"
            )
        
        # Получаем ответ от ИИ
        answer = ai_agent.answer_question(request.question, tools)
        
        return {
            "question": request.question,
            "answer": answer,
            "tools_count": len(tools),
            "sheet_id": sheet_id,
            "model": settings.model_config.model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
def get_config():
    """Получить конфигурацию системы"""
    return {
        "model": {
            "name": settings.model_config.model_name,
            "max_tokens": settings.model_config.max_tokens,
            "temperature": settings.model_config.temperature,
            "thinking_enabled": False
        },
        "api": {
            "base_url": settings.OPENAI_API_BASE,
            "configured": bool(settings.OPENAI_API_KEY)
        },
        "google_sheets": {
            "configured": bool(settings.GOOGLE_CLIENT_ID)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT,
        log_level="info"
    )
