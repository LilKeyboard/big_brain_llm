import requests
from dotenv import load_dotenv
import os

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_TOKEN = os.getenv('PERSONAL_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')

if not all([TELEGRAM_TOKEN, API_TOKEN]):
    raise ValueError("Brak wymaganych zmiennych środowiskowych (TELEGRAM_TOKEN lub API_TOKEN)")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def get_updates(offset=None):
    """Pobieranie aktualizacji z Telegrama"""
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset} if offset else {}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    """Wysyłanie wiadomości przez Telegram"""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()

def send_message_to_api(message):
    """Wysyłanie wiadomości do lokalnego API"""
    url = "http://localhost:3000/api/ask"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    payload = {
        "messages": [{"role": "user", "content": message}]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status kod API: {response.status_code}")
        print(f"Odpowiedź API: {response.text}")
        return response.json()
    except Exception as e:
        print(f"Błąd podczas wysyłania do API: {str(e)}")
        return {"error": str(e)}

def handle_message(message):
    """Obsługa otrzymanej wiadomości"""
    try:
        api_response = send_message_to_api(message)
        print(f"Otrzymana odpowiedź: {api_response}")
        
        if 'response' in api_response:
            return api_response['response']
        elif 'error' in api_response:
            return f"Wystąpił błąd: {api_response['error']}"
        else:
            return "Nieoczekiwana struktura odpowiedzi od API."
    except Exception as e:
        print(f"Błąd w handle_message: {str(e)}")
        return f"Wystąpił błąd podczas przetwarzania: {str(e)}"

def poll_updates():
    """Główna pętla bota"""
    print("Bot started...")
    last_update_id = None
    while True:
        try:
            updates = get_updates(offset=last_update_id)
            for update in updates.get('result', []):
                message_data = update.get('message', {})
                chat_id = message_data.get('chat', {}).get('id')

                if 'text' in message_data:
                    message = message_data['text']
                    print(f"\nOtrzymana wiadomość: {message}")
                    
                    response = handle_message(message)
                    print(f"Wysyłana odpowiedź: {response}")
                    
                    send_message(chat_id, response)
                else:
                    print("Otrzymano wiadomość, która nie jest tekstem.")
                    send_message(chat_id, "Przepraszam, obsługuję tylko wiadomości tekstowe.")
                
                last_update_id = update['update_id'] + 1
        except KeyboardInterrupt:
            print("\nBot zatrzymany przez użytkownika")
            break
        except Exception as e:
            print(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    poll_updates() 
