# Amazon LSTM Stock Price Prediction API

API RESTful construída com FastAPI para servir predições de preços de ações da Amazon usando um modelo LSTM treinado com TensorFlow.

## 🌐 Live Demo

**🔗 Interface Web:** [https://amazon-ltsm-yfinance-production.up.railway.app/](https://amazon-ltsm-yfinance-production.up.railway.app/)
**📚 Documentação API:** [https://amazon-ltsm-yfinance-production.up.railway.app/docs](https://amazon-ltsm-yfinance-production.up.railway.app/docs)

## 🚀 Features

- ✅ **Interface web moderna** com identidade visual Amazon
- ✅ **Predição de preços** com modelo LSTM
- ✅ **Deploy na Railway** (suporta TensorFlow)
- ✅ **Upload de CSV** ou entrada manual via JSON
- ✅ **Monitoramento** com logs em tempo real
- ✅ **Validação robusta** de entrada com Pydantic
- ✅ **Health checks** e métricas
- ✅ **CI/CD automático** via GitHub

## 📋 Requisitos

- Python 3.12+
- Modelo LSTM treinado (`amzn_lstm_model.keras`)
- Scaler treinado (`scaler.save`)
- Conta na Railway (gratuita)
- Repositório no GitHub

## 🏗️ Arquitetura

```
amazon-ltsm-yfinance/
├── api/
│   └── index.py              # Entrypoint FastAPI (serverless)
├── app/
│   ├── __init__.py
│   ├── inference.py          # Pipeline de inferência
│   ├── model_loader.py       # Singleton para modelo/scaler
│   ├── schemas.py            # Pydantic schemas
│   ├── settings.py           # Configurações
│   └── monitoring.py         # Logs e métricas
├── artifacts/
│   ├── amzn_lstm_model.keras # Modelo treinado
│   └── scaler.save           # Scaler joblib
├── tests/
│   ├── test_api.py           # Testes automatizados
│   └── test_payload.json     # Payload de exemplo
├── requirements.txt
├── Procfile
├── railway.toml
└── README.md
```

## 🔧 Setup Local

### 1. Clone o repositório

```bash
git clone <seu-repo>
cd amazon-ltsm-yfinance
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Coloque os artefatos do modelo

Certifique-se de ter os arquivos na pasta `artifacts/`:
- `amzn_lstm_model.keras` - Modelo LSTM treinado
- `scaler.save` - Scaler para normalização

### 5. Execute localmente

```bash
uvicorn api.index:app --reload
```

A API estará disponível em: `http://localhost:8000`

## 🌐 Interface Web

Acesse `http://localhost:8000` no navegador para usar a **interface web interativa**!

**Features:**
- 📤 Upload de arquivo CSV (drag & drop)
- ⌨️ Entrada manual de dados (JSON)
- 🎨 Design com identidade visual Amazon
- 📱 Totalmente responsivo
- ✅ Validações automáticas em tempo real


## 📡 Endpoints

### `GET /`
**Interface Web HTML** - Acesse no navegador para usar a interface gráfica

### `GET /api`
Informações básicas da API (JSON)

**Resposta:**
```json
{
  "name": "Amazon LSTM Stock Price Prediction API",
  "version": "1.0",
  "status": "online",
  "endpoints": {...}
}
```

---

### `POST /predict`
Prediz o próximo preço de fechamento

**Entrada:** JSON com 60+ candles históricos (OHLCV)

```json
{
  "data": [
    {
      "open": 150.2,
      "high": 152.1,
      "low": 149.8,
      "close": 151.5,
      "volume": 1000000
    },
    // ... mais 59 registros
  ]
}
```

**Saída:**
```json
{
  "prediction": 152.3,
  "timestamp": "2026-01-07T10:30:00Z",
  "model_version": "1.0"
}
```

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @tests/test_payload.json
```

---

### `GET /health`
Verifica status da API

**Resposta:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true,
  "timestamp": "2026-01-07T10:30:00Z"
}
```

---

### `GET /model/info`
Informações do modelo

**Resposta:**
```json
{
  "model_version": "1.0",
  "lookback": 60,
  "features": ["open", "high", "low", "close", "volume"],
  "target": "close"
}
```

---

### `GET /metrics`
Métricas da aplicação

**Resposta:**
```json
{
  "metrics": {
    "total_requests": 42,
    "total_predictions": 38,
    "total_errors": 2,
    "total_cold_starts": 1
  },
  "model_info": {...},
  "settings": {...}
}
```

## 🧪 Testes

### Executar todos os testes

```bash
pytest tests/test_api.py -v
```

### Testar endpoint específico

```bash
# Health check
curl http://localhost:8000/health

# Predição com payload de exemplo
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @tests/test_payload.json
```

## 📊 Monitoramento

### Logs Estruturados

Todos os logs são em formato JSON para melhor análise:

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "level": "INFO",
  "message": "Operação concluída: full_inference_pipeline",
  "operation": "full_inference_pipeline",
  "duration_seconds": 0.234,
  "success": true
}
```


## 📝 Notas Técnicas

### Modelo LSTM

- **Lookback:** 60 dias históricos
- **Features:** Open, High, Low, Close, Volume
- **Target:** Preço de fechamento (Close) do próximo dia
- **Normalização:** MinMaxScaler ou StandardScaler

### Pipeline de Inferência

1. Validação dos dados (≥60 registros, features válidas)
2. Extração das features (OHLCV)
3. Seleção dos últimos 60 registros
4. Normalização com scaler
5. Reshape para formato LSTM: `(1, 60, 5)`
6. Predição com modelo
7. Desnormalização do resultado

## 📜 Licença

Este projeto é parte de um trabalho acadêmico da Pós-Tech da FIAP.
