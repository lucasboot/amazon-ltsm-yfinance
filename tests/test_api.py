"""
Testes básicos da API
"""
import pytest
from fastapi.testclient import TestClient
import json

# Nota: Para rodar os testes, você precisa ter o modelo e scaler nos artifacts/
# Os testes vão falhar se os arquivos não existirem


def test_root():
    """Teste do endpoint raiz"""
    from api.index import app
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "online"


def test_health():
    """Teste do endpoint de health check"""
    from api.index import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "scaler_loaded" in data
    assert "timestamp" in data


def test_model_info():
    """Teste do endpoint de informações do modelo"""
    from api.index import app
    client = TestClient(app)
    
    response = client.get("/model/info")
    assert response.status_code == 200
    
    data = response.json()
    assert "model_version" in data
    assert "lookback" in data
    assert "features" in data
    assert "target" in data
    assert data["lookback"] == 60
    assert len(data["features"]) == 5


def test_metrics():
    """Teste do endpoint de métricas"""
    from api.index import app
    client = TestClient(app)
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "metrics" in data
    assert "model_info" in data
    assert "settings" in data


def test_predict_insufficient_data():
    """Teste de predição com dados insuficientes"""
    from api.index import app
    client = TestClient(app)
    
    # Enviar apenas 10 candles (menos que os 60 necessários)
    payload = {
        "data": [
            {
                "open": 150.0,
                "high": 151.0,
                "low": 149.0,
                "close": 150.5,
                "volume": 1000000
            }
        ] * 10
    }
    
    response = client.post("/predict", json=payload)
    # Deve retornar erro 422 (validação do Pydantic) ou 400 (validação customizada)
    assert response.status_code in [400, 422]


def test_predict_invalid_data():
    """Teste de predição com dados inválidos"""
    from api.index import app
    client = TestClient(app)
    
    # Dados com high < low (inválido)
    payload = {
        "data": [
            {
                "open": 150.0,
                "high": 149.0,  # high menor que low
                "low": 151.0,
                "close": 150.5,
                "volume": 1000000
            }
        ] * 60
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validação do Pydantic


# Este teste só passa se o modelo estiver carregado
@pytest.mark.skipif(True, reason="Requer modelo e scaler nos artifacts/")
def test_predict_valid_data():
    """Teste de predição com dados válidos"""
    from api.index import app
    client = TestClient(app)
    
    # Dados válidos com 60 candles
    payload = {
        "data": [
            {
                "open": 150.0 + i,
                "high": 152.0 + i,
                "low": 149.0 + i,
                "close": 151.0 + i,
                "volume": 1000000
            }
            for i in range(60)
        ]
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "prediction" in data
    assert "timestamp" in data
    assert "model_version" in data
    assert isinstance(data["prediction"], float)
    assert data["prediction"] > 0


if __name__ == "__main__":
    # Executar testes com: pytest tests/test_api.py -v
    pytest.main([__file__, "-v"])



