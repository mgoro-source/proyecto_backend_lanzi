from src.db import ejecutar_consulta, ejecutar_mutacion

def obtener_todos_los_socios(nombre: str = None, activo: bool = None, limite: int = 10, offset: int = 0) -> list[dict]:
    
    sql = "SELECT id_socio, nombre_socio, email_socio, activo FROM socios WHERE 1=1"
    parametros = {}
    
    if nombre:
        sql += " AND LOWER(nombre_socio) LIKE LOWER(:nombre)"
        parametros["nombre"] = f"%{nombre}%"
    if activo is not None:
        sql += " AND activo = :activo"
        parametros["activo"] = activo
        
    sql += " ORDER BY id_socio LIMIT :limite OFFSET :offset"
    parametros["limite"] = limite
    parametros["offset"] = offset
    
    return ejecutar_consulta(sql, parametros)

def contar_socios(nombre: str = None, activo: bool = None) -> int:
    
    sql = "SELECT COUNT(*) as total FROM socios WHERE 1=1"
    parametros = {}
    
    if nombre:
        sql += " AND LOWER(nombre_socio) LIKE LOWER(:nombre)"
        parametros["nombre"] = f"%{nombre}%"
    if activo is not None:
        sql += " AND activo = :activo"
        parametros["activo"] = activo
        
    resultado = ejecutar_consulta(sql, parametros)
    
    return resultado[0]["total"] if resultado else 0

def obtener_socio_por_id(id_socio: int) -> dict | None:
    
    sql = "SELECT id_socio, nombre_socio, email_socio, activo FROM socios WHERE id_socio = :id_socio"
    resultados = ejecutar_consulta(sql, {"id_socio": id_socio})
    
    return resultados[0] if resultados else None

def obtener_socio_por_email(email_socio: str) -> dict | None:
    
    sql = "SELECT id_socio, nombre_socio, email_socio, activo FROM socios WHERE email_socio = :email_socio"
    resultados = ejecutar_consulta(sql, {"email_socio": email_socio})
    
    return resultados[0] if resultados else None

def insertar_socio(nombre_socio: str, email_socio: str, activo: bool) -> int:
    
    sql = """
          INSERT INTO socios (nombre_socio, email_socio, activo)
          VALUES (:nombre_socio, :email_socio, :activo)
          """
    return ejecutar_mutacion(sql, {'nombre_socio': nombre_socio, 'email_socio': email_socio, 'activo': activo})

def actualizar_socio(id_socio: int, nombre_socio: str, email_socio: str, activo: bool) -> None:
    
    sql = """
          UPDATE socios 
          SET nombre_socio = :nombre_socio, 
              email_socio = :email_socio, 
              activo = :activo
          WHERE id_socio = :id_socio
          """
    ejecutar_mutacion(sql, {'id_socio': id_socio, 'nombre_socio': nombre_socio, 'email_socio': email_socio, 'activo': activo})
    