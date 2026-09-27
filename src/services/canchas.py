from ..constantes import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_DEPORTE_NOT_FOUND,
    ERROR_CODE_CANCHA_HAS_RESERVATIONS,
    ERROR_CODE_INTERNAL_ERROR,
    LIMIT_DEFAULT,
    OFFSET_DEFAULT,
)
from ..repositories import canchas as repo_canchas


def listar_canchas(filtros):
    try:
        canchas, err_repo = repo_canchas.obtener_todas(filtros)
        if err_repo:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_repo}
        
        total, err_count = repo_canchas.contar_todas(filtros)
        if err_count:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_count}
    
        limit = filtros.get('_limit', LIMIT_DEFAULT)
        offset = filtros.get('_offset', OFFSET_DEFAULT)

        resultado = {
            "canchas": canchas,
            "_limit": limit,
            "_offset": offset,
            "_total": total,
            "_links": _construir_links_paginacion('/canchas', limit, offset, total, filtros)
        }

        return resultado, None

    except Exception as e:
        return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": f"Error inesperado en servicio: {str(e)}"}

    
def crear_cancha(datos):
    try:
        existe_deporte, err_dep = repo_canchas.existe_deporte(datos['id_deporte'])
        if err_dep:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_dep}
        
        if not existe_deporte:
            return None, {
                "code": ERROR_CODE_DEPORTE_NOT_FOUND,
                "description": f"El deporte con ID {datos['id_deporte']} no existe en el sistema."
            }
        
        cancha_id, err_insert = repo_canchas.insertar(datos)
        if err_insert:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_insert}

        cancha_creada, err_get = repo_canchas.obtener_por_id(cancha_id)
        if err_get or not cancha_creada:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": "Error al recuperar la cancha creada."}
        
        return cancha_creada, None
    
    except Exception as e:
        return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": f"Error al crear cancha: {str(e)}"}


def consultar_canchas_disponibles(params):
    try:
        canchas, err_repo = repo_canchas.obtener_disponibles(params)
        if err_repo:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_repo}
        
        total, err_count = repo_canchas.contar_disponibles(params)
        if err_count:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_count}
        
        limit = params.get('_limit', LIMIT_DEFAULT)
        offset = params.get('_offset', OFFSET_DEFAULT)

        resultado = {
            "canchas": canchas,
            "_limit": limit,
            "_offset": offset,
            "_total": total
        }

        return resultado, None
    
    except Exception as e:
        return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": f"Error al consultar disponibilidad: {str(e)}"}

    
def obtener_cancha_por_id(cancha_id):
    try:
        cancha, err_repo = repo_canchas.obtener_por_id(cancha_id)
        if err_repo:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_repo}
        if not cancha:
            return None, {
                "code": ERROR_CODE_CANCHA_NOT_FOUND,
                "description": f"La cancha con ID {cancha_id} no existe."
            }
        
        return cancha, None
    except Exception as e:
        return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": f"Error al buscar cancha: {str(e)}"}

    
def actualizar_cancha(cancha_id, datos):
    try:
        cancha, err_get = repo_canchas.obtener_por_id(cancha_id)
        if err_get:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_get}
        
        if not cancha:
            return None, {
                "code": ERROR_CODE_CANCHA_NOT_FOUND,
                "description": f"La cancha con ID {cancha_id} no existe."
            }
        
        exito, err_update = repo_canchas.actualizar(cancha_id, datos)
        if err_update:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_update}
        
        return True, None
    
    except Exception as e:
        return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": f"Error al actualizar cancha: {str(e)}"}

    
def eliminar_cancha(cancha_id):
    try:
        cancha, err_get = repo_canchas.obtener_por_id(cancha_id)
        if err_get:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_get}

        if not cancha:
            return None, {
                "code": ERROR_CODE_CANCHA_NOT_FOUND,
                "description": f"La cancha con ID {cancha_id} no existe."
            }
        
        tiene_reservas, err_res = repo_canchas.tiene_reservas_asociadas(cancha_id)
        if err_res:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_res}
        
        if tiene_reservas:
            return None, {
                "code": ERROR_CODE_CANCHA_HAS_RESERVATIONS,
                "description": f"No se puede eliminar la cancha con ID {cancha_id} porque posee reservas registradas."
            }
        
        exito, err_del = repo_canchas.eliminar(cancha_id)
        if err_del:
            return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": err_del}
        
        return True, None
    
    except Exception as e:
        return None, {"code": ERROR_CODE_INTERNAL_ERROR, "description": f"Error al eliminar cancha: {str(e)}"}

    
def _construir_links_paginacion(endpoint, limit, offset, total, filtros):
    base_url = f"{endpoint}?_limit={limit}"
    for k, v in filtros.items():
        if k not in ['_limit', '_offset'] and v is not None:
            base_url += f"&{k}={v}"

        links = {"self": f"{base_url}&_offset={offset}"}
        if offset + limit < total:
            links["next"] = f"{base_url}&_offset={offset + limit}"
        if offset > 0:
            prev_offset = max(0, offset - limit)
            links["prev"] = f"{base_url}&_offset={prev_offset}"
            
    return links