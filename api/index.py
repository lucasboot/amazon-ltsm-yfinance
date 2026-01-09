"""
FastAPI entrypoint para Vercel serverless
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.schemas import (
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    ErrorResponse
)
from app.inference import inference_pipeline
from app.model_loader import (
    load_model_and_scaler,
    is_model_loaded,
    is_scaler_loaded,
    get_model_info
)
from app.settings import settings
from app.monitoring import (
    structured_log,
    log_prediction_request,
    log_model_loading,
    log_health_check,
    log_error,
    metrics
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    Carrega modelo e scaler no startup
    """
    structured_log.info("Iniciando aplicação", event="startup")
    
    try:
        start_time = time.time()
        
        # Carregar modelo e scaler
        model, scaler = load_model_and_scaler()
        
        duration = time.time() - start_time
        
        log_model_loading(
            model_loaded=True,
            scaler_loaded=True,
            duration=duration
        )
        
        structured_log.info(
            "Aplicação iniciada com sucesso",
            event="startup_complete",
            duration_seconds=round(duration, 3)
        )
        
    except Exception as e:
        structured_log.error(
            "Erro ao iniciar aplicação",
            event="startup_error",
            error=str(e)
        )
    
    yield
    
    structured_log.info("Encerrando aplicação", event="shutdown")
    metrics.log_metrics()


app = FastAPI(
    title="Amazon LSTM Stock Price Prediction API",
    description="API para predição de preços de ações usando LSTM",
    version=settings.MODEL_VERSION,
    lifespan=lifespan
)

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """Serve a interface web HTML"""
    html_path = TEMPLATES_DIR / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    else:
        return {
            "name": "Amazon LSTM Stock Price Prediction API",
            "version": settings.MODEL_VERSION,
            "status": "online",
            "message": "Interface HTML não encontrada. Use /api para info da API."
        }


@app.get("/api", tags=["Root"])
async def api_info():
    """Endpoint para informações da API (JSON)"""
    return {
        "name": "Amazon LSTM Stock Price Prediction API",
        "version": settings.MODEL_VERSION,
        "status": "online",
        "endpoints": {
            "web_interface": "/",
            "predict": "/predict",
            "health": "/health",
            "model_info": "/model/info",
            "metrics": "/metrics",
            "docs": "/docs"
        },
        "description": "API RESTful para predição de preços de ações usando modelo LSTM"
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"],
    summary="Predizer próximo preço",
    description=f"Recebe {settings.LOOKBACK} candles históricos e prediz o próximo preço de fechamento"
)
async def predict(request: PredictionRequest):
    """
    Endpoint principal de predição
    
    Args:
        request: PredictionRequest com dados históricos
        
    Returns:
        PredictionResponse com a predição
        
    Raises:
        HTTPException: Se houver erro na predição
    """
    start_time = time.time()
    
    try:
        structured_log.info(
            "Recebida requisição de predição",
            endpoint="/predict",
            num_records=len(request.data)
        )
        
        if not is_model_loaded() or not is_scaler_loaded():
            structured_log.warning(
                "Modelo não carregado, tentando carregar...",
                model_loaded=is_model_loaded(),
                scaler_loaded=is_scaler_loaded()
            )
            
            try:
                load_model_and_scaler()
            except Exception as e:
                log_error(e, context="lazy_model_loading")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Modelo não disponível. Tente novamente em alguns segundos."
                )
        
        prediction = inference_pipeline.predict(request.data)
        
        duration = time.time() - start_time
        log_prediction_request(
            num_records=len(request.data),
            duration=duration,
            success=True
        )
        
        return prediction
        
    except ValueError as e:
        duration = time.time() - start_time
        log_prediction_request(
            num_records=len(request.data),
            duration=duration,
            success=False
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        duration = time.time() - start_time
        log_prediction_request(
            num_records=len(request.data),
            duration=duration,
            success=False
        )
        log_error(e, context="/predict")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar predição: {str(e)}"
        )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Verifica se a API e o modelo estão funcionando"
)
async def health():
    """
    Health check endpoint
    
    Returns:
        HealthResponse com status da aplicação
    """
    model_loaded = is_model_loaded()
    scaler_loaded = is_scaler_loaded()
    
    if model_loaded and scaler_loaded:
        status_str = "healthy"
    elif not model_loaded and not scaler_loaded:
        status_str = "unhealthy"
    else:
        status_str = "degraded"
    
    log_health_check(
        status=status_str,
        model_loaded=model_loaded,
        scaler_loaded=scaler_loaded
    )
    
    return HealthResponse(
        status=status_str,
        model_loaded=model_loaded,
        scaler_loaded=scaler_loaded
    )


@app.get(
    "/model/info",
    response_model=ModelInfoResponse,
    tags=["Model"],
    summary="Informações do modelo",
    description="Retorna metadados e configurações do modelo"
)
async def model_info():
    """
    Retorna informações sobre o modelo
    
    Returns:
        ModelInfoResponse com metadados do modelo
    """
    return ModelInfoResponse(
        model_version=settings.MODEL_VERSION,
        lookback=settings.LOOKBACK,
        features=settings.FEATURES,
        target=settings.TARGET
    )


@app.get(
    "/templates/example.csv",
    tags=["Static"],
    summary="CSV de exemplo",
    description="Baixa arquivo CSV de exemplo para testes"
)
async def get_example_csv():
    """
    Serve o arquivo CSV de exemplo
    
    Returns:
        FileResponse com o CSV
    """
    csv_path = TEMPLATES_DIR / "example.csv"
    if csv_path.exists():
        return FileResponse(
            str(csv_path),
            media_type="text/csv",
            filename="example.csv"
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="CSV de exemplo não encontrado"
    )


@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="Métricas da aplicação",
    description="Retorna métricas de uso da API"
)
async def get_metrics():
    """
    Retorna métricas da aplicação
    
    Returns:
        Dict com métricas
    """
    return {
        "metrics": metrics.get_metrics(),
        "model_info": get_model_info(),
        "settings": settings.get_model_info()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas
    """
    log_error(exc, context="global_exception_handler")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


