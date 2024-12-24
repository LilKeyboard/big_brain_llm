from typing import Callable, Dict, Any
from functools import wraps
from flask import request, jsonify
import time
import os

def chat_limiter(f: Callable) -> Callable:
    rate_limits: Dict[str, float] = {}
    window_ms = 10 * 1000  # 10 seconds

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # Get client IP
        forwarded_for = request.headers.get('X-Forwarded-For')
        client_ip = forwarded_for.split(',')[0] if forwarded_for else request.remote_addr or '127.0.0.1'
        
        current_time = time.time() * 1000
        last_request_time = rate_limits.get(client_ip, 0)
        
        if current_time - last_request_time < window_ms:
            return jsonify({'error': 'Too many requests'}), 429
        
        rate_limits[client_ip] = current_time
        return await f(*args, **kwargs)
    
    return decorated_function

def auth_middleware(f: Callable) -> Callable:
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized: No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        expected_token = os.getenv('PERSONAL_API_KEY')
        
        if not token or token != expected_token:
            return jsonify({'error': 'Unauthorized: Invalid token'}), 401
        
        return await f(*args, **kwargs)
    
    return decorated_function

def validation_middleware(f: Callable) -> Callable:
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        data = request.get_json()
        messages = data.get('messages', [])
        
        if not isinstance(messages, list) or not messages:
            return jsonify({'error': 'Invalid request: messages must be a non-empty array'}), 400
        
        def is_valid_message(msg: Dict[str, Any]) -> bool:
            return (isinstance(msg.get('content'), str) and 
                   msg.get('content').strip() and 
                   msg.get('role') in ['user', 'assistant'])
        
        if not all(is_valid_message(msg) for msg in messages):
            return jsonify({'error': 'Invalid request: each message must have a non-empty content and a role of either "user" or "assistant"'}), 400
        
        return await f(*args, **kwargs)
    
    return decorated_function