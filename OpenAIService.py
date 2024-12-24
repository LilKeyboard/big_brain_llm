from typing import List, Dict, Any, Union, AsyncIterator
import openai
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types import Embedding
import tiktoken
import json

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI()
        self.tokenizers = {}
        self.IM_START = "<|im_start|>"
        self.IM_END = "<|im_end|>"
        self.IM_SEP = "<|im_sep|>"

    def get_tokenizer(self, model_name: str) -> tiktoken.Encoding:
        if model_name not in self.tokenizers:
            self.tokenizers[model_name] = tiktoken.encoding_for_model(model_name)
        return self.tokenizers[model_name]

    def count_tokens(self, messages: List[Dict[str, str]], model: str = 'gpt-4o-mini') -> int:
        tokenizer = self.get_tokenizer(model)
        
        formatted_content = ''
        for message in messages:
            formatted_content += f"{self.IM_START}{message['role']}{self.IM_SEP}{message.get('content', '')}{self.IM_END}"
        formatted_content += f"{self.IM_START}assistant{self.IM_SEP}"
        
        return len(tokenizer.encode(formatted_content))

    async def completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = "gpt-4o-mini",
                        stream: bool = False,
                        temperature: float = 0,
                        json_mode: bool = False,
                        max_tokens: int = 4096) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            return response
        except Exception as error:
            print("Error in OpenAI completion:", error)
            raise

    def parse_json_response(self, response: ChatCompletion) -> Dict[str, Any]:
        try:
            content = response.choices[0].message.content
            if not content:
                raise ValueError('Invalid response structure')
            return json.loads(content)
        except Exception as error:
            print('Error parsing JSON response:', error)
            return {'error': 'Failed to process response', 'result': False}

    async def create_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as error:
            print("Error creating embedding:", error)
            raise