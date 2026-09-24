import logging
from ..repositories.deportes import (
    obtener_todos_los_deportes
)

logger = logging.getLogger(__name__)

def construir_deporte(deporte: dict) -> dict:
    
    return {
        'id_deporte':   deporte['id_deporte'],
        'nombre_deporte':   deporte['nombre_deporte'],
        
    }


def listar_deportes() -> list[dict]:
    
    return [construir_deporte(a) for a in obtener_todos_los_deportes()]
