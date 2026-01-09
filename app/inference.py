"""
Pipeline de inferência para predições do modelo LSTM
"""
import logging
from typing import List
import numpy as np

from app.schemas import CandleData, PredictionResponse
from app.model_loader import get_model, get_scaler
from app.settings import settings
from app.monitoring import track_time, log_error

logger = logging.getLogger(__name__)


class InferencePipeline:
    """Pipeline completo de inferência"""
    
    def __init__(self):
        """Inicializa o pipeline"""
        self.lookback = settings.LOOKBACK
        self.features = settings.FEATURES
        self.n_features = len(self.features)
    
    def _validate_input(self, data: List[CandleData]) -> None:
        """
        Valida os dados de entrada
        
        Args:
            data: Lista de candles
            
        Raises:
            ValueError: Se os dados não são válidos
        """
        if len(data) < self.lookback:
            raise ValueError(
                f"Dados insuficientes. Esperado >= {self.lookback}, "
                f"recebido: {len(data)}"
            )
        
        logger.info(f"Validação OK: {len(data)} registros recebidos")
    
    def _prepare_features(self, data: List[CandleData]) -> np.ndarray:
        """
        Converte os dados de entrada em array numpy com as features corretas
        
        Args:
            data: Lista de candles
            
        Returns:
            Array numpy com shape (n_samples, n_features)
        """
        features_list = []
        
        for candle in data:
            features = [
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume
            ]
            features_list.append(features)
        
        X = np.array(features_list, dtype=np.float32)
        logger.info(f"Features preparadas: shape={X.shape}")
        
        return X
    
    def _get_last_sequence(self, X: np.ndarray) -> np.ndarray:
        """
        Extrai os últimos LOOKBACK registros
        
        Args:
            X: Array com todos os dados
            
        Returns:
            Array com últimos LOOKBACK registros
        """
        sequence = X[-self.lookback:]
        logger.info(f"Sequência extraída: shape={sequence.shape}")
        
        return sequence
    
    @track_time("scale_features")
    def _scale_features(self, X: np.ndarray) -> np.ndarray:
        """
        Aplica normalização nas features
        
        Args:
            X: Array com features não normalizadas
            
        Returns:
            Array com features normalizadas
        """
        scaler = get_scaler()
        X_scaled = scaler.transform(X)
        
        logger.info(
            f"Features normalizadas: "
            f"min={X_scaled.min():.3f}, max={X_scaled.max():.3f}"
        )
        
        return X_scaled
    
    def _reshape_for_lstm(self, X: np.ndarray) -> np.ndarray:
        """
        Reshape para formato esperado pelo LSTM
        
        Args:
            X: Array 2D (timesteps, features)
            
        Returns:
            Array 3D (1, timesteps, features)
        """
        X_reshaped = X.reshape(1, self.lookback, self.n_features)
        logger.info(f"Reshape para LSTM: shape={X_reshaped.shape}")
        
        return X_reshaped
    
    @track_time("model_prediction")
    def _predict(self, X: np.ndarray) -> float:
        """
        Executa a predição do modelo
        
        Args:
            X: Array preparado para inferência
            
        Returns:
            Predição (valor normalizado)
        """
        model = get_model()
        prediction = model.predict(X, verbose=0)
        pred_value = float(prediction[0][0] if prediction.ndim > 1 else prediction[0])
        
        logger.info(f"Predição (normalizada): {pred_value:.6f}")
        
        return pred_value
    
    def _denormalize_prediction(self, pred_normalized: float) -> float:
        """
        Desnormaliza a predição para o valor real do preço
        
        Args:
            pred_normalized: Valor predito normalizado
            
        Returns:
            Valor predito no preço real
        """
        scaler = get_scaler()
        
        dummy_array = np.zeros((1, self.n_features))
        dummy_array[0, 3] = pred_normalized
        
        denormalized = scaler.inverse_transform(dummy_array)
        pred_real = float(denormalized[0, 3])
        
        logger.info(f"Predição (desnormalizada): {pred_real:.2f}")
        
        return pred_real
    
    @track_time("full_inference_pipeline")
    def predict(self, data: List[CandleData]) -> PredictionResponse:
        """
        Pipeline completo de predição
        
        Args:
            data: Lista de candles históricos
            
        Returns:
            PredictionResponse com a predição
            
        Raises:
            ValueError: Se os dados são inválidos
            RuntimeError: Se houver erro na predição
        """
        try:
            self._validate_input(data)
            X = self._prepare_features(data)
            X_sequence = self._get_last_sequence(X)
            X_scaled = self._scale_features(X_sequence)
            X_reshaped = self._reshape_for_lstm(X_scaled)
            pred_normalized = self._predict(X_reshaped)
            pred_real = self._denormalize_prediction(pred_normalized)
            
            response = PredictionResponse(
                prediction=pred_real,
                model_version=settings.MODEL_VERSION
            )
            
            logger.info(
                f"Pipeline concluído com sucesso! "
                f"Predição: {pred_real:.2f}"
            )
            
            return response
            
        except ValueError as e:
            log_error(e, context="validation")
            raise
        except Exception as e:
            log_error(e, context="inference_pipeline")
            raise RuntimeError(f"Erro na predição: {str(e)}") from e


inference_pipeline = InferencePipeline()
