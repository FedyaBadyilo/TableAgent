import os
from typing import List, Dict
from openai import OpenAI
from src.config.settings import settings

class AIAgent:
    def __init__(self):
        """Инициализация ИИ-агента с конфигурацией glm-4.5-flash"""
        self.config = settings.model_config
    
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

    
    def answer_question(self, question: str, tools_data: List[Dict]) -> str:
        """Ответ на вопрос на основе данных об инструментах"""
        
        # Формируем контекст
        context = self._format_tools_context(tools_data)
        
        # Создаем промпт
        user_prompt = f"""
        Доступные инструменты:
        {context}
        
        Вопрос пользователя: {question}
        """
        # Подготавливаем параметры для glm-4.5-flash
        request_params = {
            "model": self.config.model_name,
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.client.chat.completions.create(**request_params)
        
        return response.choices[0].message.content
            
    def _format_tools_context(self, tools_data: List[Dict]) -> str:
        """Форматирование данных об инструментах для контекста"""
        context = ""
        for i, tool in enumerate(tools_data, 1):
            context += f"{i}. {tool['name']}\n"
            context += f"   Ссылка: {tool['url']}\n"
            if tool.get('description'):
                context += f"   Описание: {tool['description']}\n"
            context += "\n"
        return context
    