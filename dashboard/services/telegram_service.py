import requests
from django.conf import settings
from dashboard.models import User

class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_notification(self, user, message):
        """Send notification to user via Telegram"""
        if not user.telegram_chat_id:
            return False
            
        try:
            response = self.send_message(user.telegram_chat_id, message)
            return response.get('ok', False)
        except Exception as e:
            print(f"Telegram notification failed: {e}")
            return False
    
    def send_message(self, chat_id, message):
        """Send message to specific chat ID"""
        url = f"{self.api_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'  # Support formatting
        }
        response = requests.post(url, data=data)
        return response.json()
    
    def send_message_with_buttons(self, chat_id, message, buttons):
        """Send message with inline keyboard"""
        url = f"{self.api_url}/sendMessage"
        keyboard = {
            'inline_keyboard': buttons
        }
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'reply_markup': keyboard
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def get_bot_info(self):
        """Get bot information"""
        url = f"{self.api_url}/getMe"
        response = requests.get(url)
        return response.json()