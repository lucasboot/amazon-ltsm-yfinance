#!/usr/bin/env python
"""
Script para testar a API localmente
Útil para verificar se tudo está funcionando antes do deploy
"""
import json
import requests
from pathlib import Path

# URL base (ajuste se necessário)
BASE_URL = "http://localhost:8000"


def test_root():
    """Testa endpoint raiz"""
    print("\n🔍 Testando GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_health():
    """Testa health check"""
    print("\n🔍 Testando GET /health")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_model_info():
    """Testa informações do modelo"""
    print("\n🔍 Testando GET /model/info")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_metrics():
    """Testa métricas"""
    print("\n🔍 Testando GET /metrics")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_predict():
    """Testa predição com payload de exemplo"""
    print("\n🔍 Testando POST /predict")
    
    # Carregar payload de teste
    payload_path = Path(__file__).parent.parent / "tests" / "test_payload.json"
    
    if not payload_path.exists():
        print(f"❌ Payload não encontrado: {payload_path}")
        return False
    
    with open(payload_path, 'r') as f:
        payload = json.load(f)
    
    print(f"Enviando {len(payload['data'])} registros...")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Predição: ${result['prediction']:.2f}")
        print(f"Response completo: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False


def test_predict_insufficient_data():
    """Testa predição com dados insuficientes (deve falhar)"""
    print("\n🔍 Testando POST /predict com dados insuficientes")
    
    payload = {
        "data": [
            {
                "open": 150.0,
                "high": 151.0,
                "low": 149.0,
                "close": 150.5,
                "volume": 1000000
            }
        ] * 10  # Apenas 10 registros (precisa de 60)
    }
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Deve retornar erro (400 ou 422)
    if response.status_code in [400, 422]:
        print("✅ Validação funcionando corretamente!")
        return True
    else:
        print("❌ Validação não está funcionando")
        return False


def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 Testando API Local")
    print("=" * 60)
    print(f"URL Base: {BASE_URL}")
    print("=" * 60)
    
    tests = [
        ("Root", test_root),
        ("Health", test_health),
        ("Model Info", test_model_info),
        ("Metrics", test_metrics),
        ("Predict (dados insuficientes)", test_predict_insufficient_data),
        ("Predict (válido)", test_predict),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Erro: Não foi possível conectar à API")
            print(f"   Certifique-se de que a API está rodando em {BASE_URL}")
            print(f"   Execute: uvicorn api.index:app --reload")
            return
        except Exception as e:
            print(f"\n❌ Erro ao executar teste {name}: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("📊 Resumo dos Testes")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    total = len(results)
    passed = sum(results.values())
    print("=" * 60)
    print(f"Total: {passed}/{total} testes passaram")
    print("=" * 60)


if __name__ == "__main__":
    main()

