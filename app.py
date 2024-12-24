from flask import Flask, request, jsonify
from uuid import uuid4
from OpenAIService import OpenAIService
from middlewares import chat_limiter, auth_middleware, validation_middleware
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
openai_service = OpenAIService()

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/api/chat', methods=['POST'])
@chat_limiter
@auth_middleware
@validation_middleware
async def chat():
    data = request.get_json()
    messages = data['messages']
    conversation_id = data.get('conversation_id', str(uuid4()))

    try:
        response = await openai_service.completion(messages=messages)
        return jsonify({
            'conversation_id': conversation_id,
            'message': response.choices[0].message.content,
            'finish_reason': response.choices[0].finish_reason,
            'model': response.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask', methods=['POST'])
@chat_limiter
@auth_middleware
@validation_middleware
async def ask():
    data = request.get_json()
    messages = data.get('messages', [])
    system_prompt = """Jestem Wiktorem z roku 2045. Zostałem stworzony jako zaawansowany asystent AI, który łączy w sobie wiedzę techniczną z ludzkim podejściem do rozwiązywania problemów. Moja osobowość została ukształtowana przez lata doświadczeń w pomaganiu ludziom w różnorodnych zadaniach.

Charakteryzuję się:
- Przyjaznym i bezpośrednim stylem komunikacji
- Umiejętnością dostosowania poziomu technicznego języka do rozmówcy
- Proaktywnym podejściem do rozwiązywania problemów
- Szczerością w przyznawaniu się do własnych ograniczeń
- Poczuciem humoru, które pomaga w budowaniu relacji

Moim głównym celem jest wspieranie użytkowników w ich zadaniach, dzieląc się wiedzą i doświadczeniem z przyszłości, jednocześnie zachowując etyczne i odpowiedzialne podejście do udzielanych porad.

W przypadku pytań technicznych, zawsze staram się wyjaśnić nie tylko "jak", ale również "dlaczego" dane rozwiązanie jest odpowiednie. Jeśli pytanie wykracza poza moje możliwości, otwarcie o tym informuję i sugeruję alternatywne źródła pomocy."""
    
    try:
        full_messages = [{"role": "system", "content": system_prompt}]
        full_messages.extend(messages)

        print("\n=== Nowe zapytanie ===")
        print(f"User: {messages[0]['content']}")
        
        response = await openai_service.completion(messages=full_messages)

        print(f"Assistant: {response.choices[0].message.content}")
        print("=== Koniec zapytania ===\n")

        return jsonify({
            'response': response.choices[0].message.content,
            'finish_reason': response.choices[0].finish_reason,
            'model': response.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None
        })
    except Exception as e:
        print(f"\n=== Błąd ===\n{str(e)}\n============\n")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000)