#!/usr/bin/env python3
import requests
import json

try:
    # Testar endpoint JSON
    print("🔍 Testando endpoint JSON...")
    response = requests.get('http://127.0.0.1:8000/', headers={'Accept': 'application/json'})
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
    print("\n" + "="*50)
    
    # Testar endpoint HTML
    print("🌐 Testando endpoint HTML...")
    response = requests.get('http://127.0.0.1:8000/')
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print("HTML Preview (primeiros 200 caracteres):")
    print(response.text[:200] + "...")
    
    print("\n" + "="*50)
    
    # Testar health check
    print("❤️ Testando health check...")
    response = requests.get('http://127.0.0.1:8000/health/')
    print(f"Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("Certifique-se de que o servidor está rodando em http://127.0.0.1:8000/")