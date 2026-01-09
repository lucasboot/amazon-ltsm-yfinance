"""
Parser de CSV para dados de candles
"""
import csv
import io
from typing import List
import logging

from app.schemas import CandleData

logger = logging.getLogger(__name__)


def parse_csv_to_candles(csv_content: str) -> List[CandleData]:
    """
    Parse CSV content to list of CandleData
    
    Args:
        csv_content: String com conteúdo do CSV
        
    Returns:
        List[CandleData]: Lista de candles parseados
        
    Raises:
        ValueError: Se o CSV for inválido
    """
    try:
        # Ler CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Validar headers
        required_fields = {'open', 'high', 'low', 'close', 'volume'}
        headers = set(field.lower().strip() for field in reader.fieldnames or [])
        
        missing_fields = required_fields - headers
        if missing_fields:
            raise ValueError(
                f"CSV inválido. Campos faltando: {', '.join(missing_fields)}. "
                f"Campos esperados: Open, High, Low, Close, Volume (case-insensitive)"
            )
        
        # Parse rows
        candles = []
        for i, row in enumerate(reader, start=2):  # linha 2 (1 é header)
            try:
                # Normalizar keys (lowercase)
                row_normalized = {k.lower().strip(): v.strip() for k, v in row.items()}
                
                candle = CandleData(
                    open=float(row_normalized['open']),
                    high=float(row_normalized['high']),
                    low=float(row_normalized['low']),
                    close=float(row_normalized['close']),
                    volume=float(row_normalized['volume'])
                )
                candles.append(candle)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Erro ao parsear linha {i}: {e}")
                raise ValueError(f"Erro na linha {i}: valores inválidos ou faltando")
        
        if len(candles) == 0:
            raise ValueError("CSV não contém dados válidos")
        
        if len(candles) < 60:
            raise ValueError(
                f"CSV deve conter pelo menos 60 registros. "
                f"Encontrado: {len(candles)}"
            )
        
        logger.info(f"CSV parseado com sucesso: {len(candles)} candles")
        return candles
        
    except csv.Error as e:
        logger.error(f"Erro ao ler CSV: {e}")
        raise ValueError(f"Formato de CSV inválido: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao parsear CSV: {e}")
        raise


def validate_csv_format(csv_content: str) -> dict:
    """
    Valida formato do CSV sem parsear completamente
    
    Args:
        csv_content: String com conteúdo do CSV
        
    Returns:
        dict: Informações de validação (is_valid, message, num_rows)
    """
    try:
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Validar headers
        required_fields = {'open', 'high', 'low', 'close', 'volume'}
        headers = set(field.lower().strip() for field in reader.fieldnames or [])
        
        missing_fields = required_fields - headers
        if missing_fields:
            return {
                "is_valid": False,
                "message": f"Campos faltando: {', '.join(missing_fields)} (esperado: Open,High,Low,Close,Volume - case-insensitive)",
                "num_rows": 0
            }
        
        # Contar linhas
        num_rows = sum(1 for _ in reader)
        
        if num_rows < 60:
            return {
                "is_valid": False,
                "message": f"Mínimo 60 linhas necessário. Encontrado: {num_rows}",
                "num_rows": num_rows
            }
        
        return {
            "is_valid": True,
            "message": "CSV válido",
            "num_rows": num_rows
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "message": f"Erro ao validar: {str(e)}",
            "num_rows": 0
        }

