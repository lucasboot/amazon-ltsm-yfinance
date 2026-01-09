"""
Pydantic schemas para validação de entrada e saída da API
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator


class CandleData(BaseModel):
    """Schema para um único candle (OHLCV)"""
    open: float = Field(..., description="Preço de abertura", gt=0)
    high: float = Field(..., description="Preço máximo", gt=0)
    low: float = Field(..., description="Preço mínimo", gt=0)
    close: float = Field(..., description="Preço de fechamento", gt=0)
    volume: float = Field(..., description="Volume negociado", ge=0)

    @field_validator('high')
    @classmethod
    def high_must_be_highest(cls, v, info):
        """Valida que high é maior ou igual aos outros preços"""
        if 'low' in info.data and v < info.data['low']:
            raise ValueError('high deve ser >= low')
        return v

    @field_validator('low')
    @classmethod
    def low_must_be_lowest(cls, v, info):
        """Valida que low é menor ou igual aos outros preços"""
        if 'high' in info.data and v > info.data['high']:
            raise ValueError('low deve ser <= high')
        return v


class PredictionRequest(BaseModel):
    """Schema para requisição de predição"""
    data: List[CandleData] = Field(
        ...,
        description="Lista de candles históricos (mínimo 60)",
        min_length=60
    )

    @field_validator('data')
    @classmethod
    def validate_data_length(cls, v):
        """Valida que temos dados suficientes"""
        if len(v) < 60:
            raise ValueError(
                f'São necessários pelo menos 60 registros, fornecido: {len(v)}'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "open": 150.2,
                        "high": 152.1,
                        "low": 149.8,
                        "close": 151.5,
                        "volume": 1000000
                    }
                ] * 60  # 60 registros
            }
        }


class PredictionResponse(BaseModel):
    """Schema para resposta de predição"""
    prediction: float = Field(..., description="Previsão do próximo preço de fechamento")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da predição")
    model_version: str = Field(default="1.0", description="Versão do modelo")
    confidence: float | None = Field(None, description="Confiança da predição (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 152.3,
                "timestamp": "2026-01-07T10:30:00Z",
                "model_version": "1.0",
                "confidence": None
            }
        }


class HealthResponse(BaseModel):
    """Schema para resposta de health check"""
    status: str = Field(..., description="Status da API")
    model_loaded: bool = Field(..., description="Se o modelo está carregado")
    scaler_loaded: bool = Field(..., description="Se o scaler está carregado")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelInfoResponse(BaseModel):
    """Schema para informações do modelo"""
    model_version: str = Field(..., description="Versão do modelo")
    lookback: int = Field(..., description="Número de períodos históricos necessários")
    features: List[str] = Field(..., description="Features esperadas pelo modelo")
    target: str = Field(..., description="Variável alvo da predição")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "model_version": "1.0",
                "lookback": 60,
                "features": ["open", "high", "low", "close", "volume"],
                "target": "close",
                "created_at": "2026-01-07T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Schema para respostas de erro"""
    error: str = Field(..., description="Mensagem de erro")
    detail: str | None = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.utcnow)



