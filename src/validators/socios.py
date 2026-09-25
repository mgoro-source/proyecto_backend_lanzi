import re
from src.constantes import (EMAIL_REGEX,
                          ERROR_CODE_EMPTY_BODY,
                          ERROR_CODE_NAME_REQUIRED,
                          ERROR_CODE_EMAIL_REQUIRED,
                          ERROR_CODE_EMAIL_INVALID,
                          ERROR_CODE_ACTIVE_INVALID,
                          ERROR_CODE_UNKNOWN_FIELD)
                         
def validar_creacion_socio(datos):
    
    validacion = None
    
    if not datos:
        validacion = ERROR_CODE_EMPTY_BODY
    elif not validar_campos(datos):
        validacion = ERROR_CODE_UNKNOWN_FIELD
    elif not "nombre" in datos or not isinstance(datos["nombre"], str) or not datos["nombre"].strip():
        validacion = ERROR_CODE_NAME_REQUIRED
    elif not "email" in datos or not isinstance(datos["email"], str) or not datos["email"].strip():
        validacion = ERROR_CODE_EMAIL_REQUIRED
    elif not bool(re.fullmatch(EMAIL_REGEX, datos["email"].strip())):
        validacion = ERROR_CODE_EMAIL_INVALID
    elif "activo" in datos and not isinstance(datos["activo"], bool):
        validacion = ERROR_CODE_ACTIVE_INVALID
    
    return validacion
        
def validar_actualizacion_socio(datos):
    
    validacion = None
    
    if not datos:
        validacion = ERROR_CODE_EMPTY_BODY
    else:
        if not validar_campos(datos):
            validacion = ERROR_CODE_UNKNOWN_FIELD
        elif "nombre" in datos and (not isinstance(datos["nombre"], str) or not datos["nombre"].strip()):
            validacion = ERROR_CODE_NAME_REQUIRED
        elif "email" in datos and (not isinstance(datos["email"], str) or not datos["email"].strip()):
            validacion = ERROR_CODE_EMAIL_REQUIRED
        elif "email" in datos and not bool(re.fullmatch(EMAIL_REGEX, datos["email"].strip())):
            validacion = ERROR_CODE_EMAIL_INVALID
        elif "activo" in datos and not isinstance(datos["activo"], bool):
            validacion = ERROR_CODE_ACTIVE_INVALID
    
    return validacion

def validar_campos(datos):
    
    campos_permitidos = {"nombre", "email", "activo"}
    validacion = True
        
    for campo in datos.keys():
        if campo not in campos_permitidos:
            validacion = False
    
    return validacion
