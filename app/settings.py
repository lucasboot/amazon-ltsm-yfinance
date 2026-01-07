"""
Configurações da aplicação
"""
import os
from pathlib import Path
from typing import List


class Settings:
    """Configurações centralizadas da aplicação"""
    
    # Versão
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "1.0")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Modelo
    LOOKBACK: int = int(os.getenv("LOOKBACK", "60"))
    FEATURES: List[str] = os.getenv(
        "FEATURES", 
        "open,high,low,close,volume"
    ).split(",")
    TARGET: str = os.getenv("TARGET", "close")
    
    # Caminhos dos artefatos
    BASE_DIR: Path = Path(__file__).parent.parent
    ARTIFACTS_DIR: Path = BASE_DIR / "artifacts"
    MODEL_PATH: Path = ARTIFACTS_DIR / "amzn_lstm_model.keras"
    SCALER_PATH: Path = ARTIFACTS_DIR / "scaler.save"
    
    # Vercel
    VERCEL_ENV: str = os.getenv("VERCEL_ENV", "development")
    IS_PRODUCTION: bool = VERCEL_ENV == "production"
    
    # Timeouts e limites
    PREDICTION_TIMEOUT: int = int(os.getenv("PREDICTION_TIMEOUT", "10"))
    MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "1"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se as configurações estão corretas"""
        errors = []
        
        # Validar que os arquivos de modelo existem
        if not cls.MODEL_PATH.exists():
            errors.append(f"Modelo não encontrado: {cls.MODEL_PATH}")
        
        if not cls.SCALER_PATH.exists():
            errors.append(f"Scaler não encontrado: {cls.SCALER_PATH}")
        
        # Validar LOOKBACK
        if cls.LOOKBACK <= 0:
            errors.append(f"LOOKBACK deve ser > 0, valor atual: {cls.LOOKBACK}")
        
        # Validar FEATURES
        if len(cls.FEATURES) == 0:
            errors.append("FEATURES não pode estar vazio")
        
        if errors:
            raise ValueError(f"Erros na configuração:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def get_model_info(cls) -> dict:
        """Retorna informações do modelo"""
        return {
            "model_version": cls.MODEL_VERSION,
            "lookback": cls.LOOKBACK,
            "features": cls.FEATURES,
            "target": cls.TARGET,
            "model_path": str(cls.MODEL_PATH),
            "scaler_path": str(cls.SCALER_PATH),
            "environment": cls.VERCEL_ENV
        }


# Instância singleton
settings = Settings()

