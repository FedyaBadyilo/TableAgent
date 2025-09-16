# src/services/google_sheets_service.py
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict
import pandas as pd

class GoogleSheetsService:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Аутентификация с Google Sheets API"""
        creds = None
        
        # Проверяем существующий токен
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        
        # Если нет валидных credentials, создаем новые
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Создаем credentials из .env переменных
                client_config = {
                    "installed": {
                        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
                    }
                }
                
                flow = InstalledAppFlow.from_client_config(client_config, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Сохраняем credentials для следующего запуска
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        self.service = build("sheets", "v4", credentials=creds)
    
    def get_sheet_data(self, spreadsheet_id: str, range_name: str = None) -> List[List]:
        """Получение данных из Google Sheets"""
        try:
            if range_name is None:
                range_name = "A:C"  # По умолчанию первые 3 колонки
            
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            values = result.get("values", [])
            return values
        except HttpError as err:
            print(f"Ошибка при получении данных: {err}")
            return []
    
    def get_tools_data(self, spreadsheet_id: str) -> List[Dict]:
        """Получение данных об инструментах в структурированном виде"""
        values = self.get_sheet_data(spreadsheet_id)
        
        if not values:
            return []
        
        tools = []
        for i, row in enumerate(values):
            if len(row) >= 2:  # Минимум название и ссылка
                tools.append({
                    'row_number': i + 1,
                    'name': row[0],
                    'url': row[1],
                    'description': row[2] if len(row) > 2 else None
                })
        
        return tools
    
    def find_tool_by_name(self, spreadsheet_id: str, tool_name: str) -> Dict:
        """Поиск инструмента по названию"""
        tools = self.get_tools_data(spreadsheet_id)
        
        for tool in tools:
            if tool_name.lower() in tool['name'].lower():
                return tool
        
        return None