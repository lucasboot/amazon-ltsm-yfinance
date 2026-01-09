"""
Monitoramento, logging e métricas da aplicação
"""
import logging
import time
from functools import wraps
from typing import Callable, Any
from datetime import datetime
import json

from app.settings import settings

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class StructuredLogger:
    """Logger estruturado para logs em JSON (melhor para Vercel)"""
    
    @staticmethod
    def log(level: str, message: str, **kwargs):
        """
        Loga mensagem estruturada
        
        Args:
            level: Nível do log (info, warning, error, etc)
            message: Mensagem principal
            **kwargs: Campos adicionais
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "message": message,
            "environment": settings.VERCEL_ENV,
            **kwargs
        }
        
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(json.dumps(log_data))
    
    @staticmethod
    def info(message: str, **kwargs):
        """Log de informação"""
        StructuredLogger.log("info", message, **kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        """Log de aviso"""
        StructuredLogger.log("warning", message, **kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        """Log de erro"""
        StructuredLogger.log("error", message, **kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs):
        """Log de debug"""
        StructuredLogger.log("debug", message, **kwargs)


# Instância global
structured_log = StructuredLogger()


def track_time(operation_name: str = None):
    """
    Decorator para rastrear tempo de execução
    
    Args:
        operation_name: Nome da operação (opcional)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            structured_log.info(
                f"Iniciando operação: {op_name}",
                operation=op_name,
                event="start"
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                structured_log.info(
                    f"Operação concluída: {op_name}",
                    operation=op_name,
                    event="complete",
                    duration_seconds=round(duration, 3),
                    success=True
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                structured_log.error(
                    f"Operação falhou: {op_name}",
                    operation=op_name,
                    event="error",
                    duration_seconds=round(duration, 3),
                    error_type=type(e).__name__,
                    error_message=str(e),
                    success=False
                )
                
                raise
        
        return wrapper
    return decorator


class RequestMetrics:
    """Classe para rastrear métricas de requisições"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "total_predictions": 0,
            "total_errors": 0,
            "total_cold_starts": 0
        }
    
    def increment_requests(self):
        """Incrementa contador de requisições"""
        self.metrics["total_requests"] += 1
    
    def increment_predictions(self):
        """Incrementa contador de predições"""
        self.metrics["total_predictions"] += 1
    
    def increment_errors(self):
        """Incrementa contador de erros"""
        self.metrics["total_errors"] += 1
    
    def increment_cold_starts(self):
        """Incrementa contador de cold starts"""
        self.metrics["total_cold_starts"] += 1
    
    def get_metrics(self) -> dict:
        """Retorna métricas atuais"""
        return self.metrics.copy()
    
    def log_metrics(self):
        """Loga métricas atuais"""
        structured_log.info(
            "Métricas da aplicação",
            **self.metrics
        )


# Instância global de métricas
metrics = RequestMetrics()


def log_prediction_request(num_records: int, duration: float, success: bool = True):
    """
    Loga detalhes de uma requisição de predição
    
    Args:
        num_records: Número de registros recebidos
        duration: Duração da operação em segundos
        success: Se a predição foi bem sucedida
    """
    structured_log.info(
        "Requisição de predição processada",
        endpoint="/predict",
        num_records=num_records,
        duration_seconds=round(duration, 3),
        success=success
    )
    
    if success:
        metrics.increment_predictions()
    else:
        metrics.increment_errors()
    
    metrics.increment_requests()


def log_model_loading(model_loaded: bool, scaler_loaded: bool, duration: float):
    """
    Loga carregamento do modelo
    
    Args:
        model_loaded: Se o modelo foi carregado
        scaler_loaded: Se o scaler foi carregado
        duration: Duração do carregamento
    """
    structured_log.info(
        "Modelo e scaler carregados",
        model_loaded=model_loaded,
        scaler_loaded=scaler_loaded,
        duration_seconds=round(duration, 3),
        event="cold_start"
    )
    
    if model_loaded and scaler_loaded:
        metrics.increment_cold_starts()


def log_error(error: Exception, context: str = None):
    """
    Loga erro com contexto
    
    Args:
        error: Exceção capturada
        context: Contexto adicional
    """
    structured_log.error(
        f"Erro capturado: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or "unknown"
    )
    
    metrics.increment_errors()


def log_health_check(status: str, model_loaded: bool, scaler_loaded: bool):
    """
    Loga health check
    
    Args:
        status: Status da aplicação
        model_loaded: Se o modelo está carregado
        scaler_loaded: Se o scaler está carregado
    """
    structured_log.info(
        "Health check executado",
        endpoint="/health",
        status=status,
        model_loaded=model_loaded,
        scaler_loaded=scaler_loaded
    )



