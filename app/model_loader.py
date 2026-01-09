"""
Carregamento do modelo e scaler com padrão Singleton
"""
import logging
from typing import Optional, Tuple
import joblib
import numpy as np

from app.settings import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Cache global para modelo e scaler (Singleton pattern)
_model_cache: Optional[object] = None
_scaler_cache: Optional[object] = None
_load_attempted: bool = False


def get_model():
    """
    Carrega o modelo LSTM (singleton)
    
    Returns:
        Modelo Keras carregado
        
    Raises:
        RuntimeError: Se o modelo não puder ser carregado
    """
    global _model_cache, _load_attempted
    
    if _model_cache is not None:
        return _model_cache
    
    if _load_attempted:
        raise RuntimeError(
            "Tentativa anterior de carregar o modelo falhou. "
            "Reinicie a aplicação."
        )
    
    _load_attempted = True
    
    try:
        # Importação lazy do TensorFlow para otimizar cold start
        import tensorflow as tf
        
        logger.info(f"Carregando modelo de: {settings.MODEL_PATH}")
        
        if not settings.MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Arquivo do modelo não encontrado: {settings.MODEL_PATH}"
            )
        
        # Carregar modelo
        _model_cache = tf.keras.models.load_model(str(settings.MODEL_PATH))
        
        logger.info(
            f"Modelo carregado com sucesso! "
            f"Input shape: {_model_cache.input_shape}"
        )
        
        return _model_cache
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {e}", exc_info=True)
        _model_cache = None
        _load_attempted = False
        raise RuntimeError(f"Falha ao carregar modelo: {str(e)}") from e


def get_scaler():
    """
    Carrega o scaler (singleton)
    
    Returns:
        Scaler scikit-learn carregado
        
    Raises:
        RuntimeError: Se o scaler não puder ser carregado
    """
    global _scaler_cache
    
    if _scaler_cache is not None:
        return _scaler_cache
    
    try:
        logger.info(f"Carregando scaler de: {settings.SCALER_PATH}")
        
        if not settings.SCALER_PATH.exists():
            raise FileNotFoundError(
                f"Arquivo do scaler não encontrado: {settings.SCALER_PATH}"
            )
        
        # Carregar scaler
        _scaler_cache = joblib.load(settings.SCALER_PATH)
        
        logger.info(
            f"Scaler carregado com sucesso! "
            f"Features: {getattr(_scaler_cache, 'n_features_in_', 'N/A')}"
        )
        
        return _scaler_cache
        
    except Exception as e:
        logger.error(f"Erro ao carregar scaler: {e}", exc_info=True)
        _scaler_cache = None
        raise RuntimeError(f"Falha ao carregar scaler: {str(e)}") from e


def load_model_and_scaler() -> Tuple[object, object]:
    """
    Carrega modelo e scaler (usado no startup da aplicação)
    
    Returns:
        Tuple[model, scaler]
        
    Raises:
        RuntimeError: Se não conseguir carregar modelo ou scaler
    """
    try:
        model = get_model()
        scaler = get_scaler()
        return model, scaler
    except Exception as e:
        logger.error(f"Erro ao carregar modelo e scaler: {e}")
        raise


def is_model_loaded() -> bool:
    """Verifica se o modelo está carregado"""
    return _model_cache is not None


def is_scaler_loaded() -> bool:
    """Verifica se o scaler está carregado"""
    return _scaler_cache is not None


def get_model_info() -> dict:
    """
    Retorna informações sobre o modelo carregado
    
    Returns:
        Dict com informações do modelo
    """
    info = {
        "model_loaded": is_model_loaded(),
        "scaler_loaded": is_scaler_loaded(),
    }
    
    if is_model_loaded():
        model = get_model()
        info.update({
            "input_shape": str(model.input_shape),
            "output_shape": str(model.output_shape),
        })
    
    if is_scaler_loaded():
        scaler = get_scaler()
        info.update({
            "n_features": getattr(scaler, 'n_features_in_', None),
        })
    
    return info


def clear_cache():
    """
    Limpa o cache (útil para testes)
    
    Atenção: Isso forçará o recarregamento do modelo na próxima chamada
    """
    global _model_cache, _scaler_cache, _load_attempted
    _model_cache = None
    _scaler_cache = None
    _load_attempted = False
    logger.info("Cache de modelo e scaler limpo")



