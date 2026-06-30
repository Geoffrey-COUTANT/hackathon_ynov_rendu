import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    """Renders the main chat interface"""
    return render_template('index.html')

@app.route('/api/health', methods=['POST'])
def health_check():
    """
    Checks the status of the target inference server.
    Accepts target API URL and type in the JSON body.
    """
    data = request.json or {}
    api_url = data.get('apiUrl', '').strip('/')
    api_type = data.get('apiType', 'ollama')
    
    if not api_url:
        return jsonify({'status': 'disconnected', 'message': 'API URL parameter is missing.'}), 400
    
    try:
        # Determine specific health endpoint based on API type
        if api_type == 'ollama':
            # Ollama root or /api/tags
            target_url = f"{api_url}/api/tags"
            response = requests.get(target_url, timeout=3)
            if response.status_code == 200:
                models = [model.get('name') for model in response.json().get('models', [])]
                return jsonify({
                    'status': 'connected',
                    'message': 'Connected to Ollama server.',
                    'models': models
                })
        elif api_type == 'openai' or api_type == 'triton_openai':
            # OpenAI compatible lists models
            target_url = f"{api_url}/v1/models"
            response = requests.get(target_url, timeout=3)
            if response.status_code == 200:
                models = [model.get('id') for model in response.json().get('data', [])]
                return jsonify({
                    'status': 'connected',
                    'message': 'Connected to OpenAI-compatible server.',
                    'models': models
                })
        
        # Fallback to simple root check
        response = requests.get(api_url, timeout=3)
        if response.status_code < 500:
            return jsonify({
                'status': 'connected',
                'message': f'Server reachable (HTTP {response.status_code}).',
                'models': []
            })
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'disconnected',
            'message': f"Unreachable: {str(e)}"
        })

    return jsonify({'status': 'disconnected', 'message': 'Server returned an invalid status.'})

@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    """
    Proxies chat generation requests to the chosen backend server.
    Bypasses CORS issues and reformats request/response.
    """
    data = request.json or {}
    api_url = data.get('apiUrl', '').strip('/')
    api_type = data.get('apiType', 'ollama')
    model_name = data.get('modelName', '')
    messages = data.get('messages', [])
    temperature = data.get('temperature', 0.7)
    
    if not api_url:
        return jsonify({'error': 'api_url_required', 'message': 'API URL is required.'}), 400
    
    if not messages:
        return jsonify({'error': 'messages_required', 'message': 'No messages provided.'}), 400

    try:
        if api_type == 'ollama':
            # Send to Ollama Chat API
            payload = {
                "model": model_name or "phi3.5-financial",
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": float(temperature)
                }
            }
            target_url = f"{api_url}/api/chat"
            response = requests.post(target_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                resp_json = response.json()
                assistant_message = resp_json.get('message', {}).get('content', '')
                return jsonify({
                    'success': True,
                    'content': assistant_message,
                    'raw': resp_json
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f"Ollama error (HTTP {response.status_code}): {response.text}"
                }), response.status_code
                
        elif api_type == 'openai' or api_type == 'triton_openai':
            # Send to OpenAI-compatible Chat API (vLLM, Ollama OpenAI compatibility layer, Triton vLLM backend, etc.)
            payload = {
                "model": model_name or "phi3.5-financial",
                "messages": messages,
                "temperature": float(temperature),
                "stream": False
            }
            target_url = f"{api_url}/v1/chat/completions"
            response = requests.post(target_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                resp_json = response.json()
                choices = resp_json.get('choices', [])
                if choices:
                    assistant_message = choices[0].get('message', {}).get('content', '')
                    return jsonify({
                        'success': True,
                        'content': assistant_message,
                        'raw': resp_json
                    })
                return jsonify({
                    'success': False,
                    'message': "Invalid response format from OpenAI-compatible server."
                }), 500
            else:
                return jsonify({
                    'success': False,
                    'message': f"Server error (HTTP {response.status_code}): {response.text}"
                }), response.status_code
                
        else:
            # Custom backend / generic proxy
            # We assume it accepts the prompt format or standard payload
            payload = {
                "messages": messages,
                "model": model_name,
                "temperature": float(temperature)
            }
            target_url = f"{api_url}/chat"
            response = requests.post(target_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'content': response.text, # standard response text
                    'raw': response.json() if response.headers.get('content-type') == 'application/json' else response.text
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f"Custom server error (HTTP {response.status_code}): {response.text}"
                }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'The request timed out. The server is taking too long to respond.'
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f"Network error connecting to the inference server: {str(e)}"
        }), 502

if __name__ == '__main__':
    # Listen on all interfaces so it's accessible externally if needed
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
