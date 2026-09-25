from datetime import datetime, timedelta
from src.exceptions import ValidationError
from src import constantes as C

FORMATO_ISO = "%Y-%m-%dT%H:%M:%S.%f-03:00"


def parsear_fecha_hora(valor: str, campo: str) -> datetime:
    """Parsea un string ISO GMT-3 con 6 decimales. Devuelve datetime naive en GMT-3."""
    if not isinstance(valor, str):
        raise ValidationError(
            f"El campo '{campo}' es inválido",
            f"'{campo}' debe ser un string en formato ISO 8601 con offset -03:00"
        )
    try:
        return datetime.strptime(valor, FORMATO_ISO)
    except ValueError:
        raise ValidationError(
            f"El campo '{campo}' es inválido",
            f"'{campo}' debe cumplir el formato YYYY-MM-DDTHH:MM:SS.ffffff-03:00"
        )


def parsear_fecha(valor: str, campo: str):
    """Parsea una fecha YYYY-MM-DD."""
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValidationError(
            f"El campo '{campo}' es inválido",
            f"'{campo}' debe tener formato YYYY-MM-DD"
        )


def parsear_bool(valor, campo: str) -> bool:
    """Acepta únicamente 'true'/'false' (string) o True/False (bool)."""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str) and valor.lower() in ("true", "false"):
        return valor.lower() == "true"
    raise ValidationError(
        f"El parámetro '{campo}' es inválido",
        f"'{campo}' debe ser 'true' o 'false'"
    )


def validar_hora_en_punto(hora_str: str, campo: str):
    """Espera 'HH:00:00' entre 08:00 y 23:00."""
    try:
        h = datetime.strptime(hora_str, "%H:%M:%S")
    except (ValueError, TypeError):
        raise ValidationError(
            f"El campo '{campo}' es inválido",
            f"'{campo}' debe tener formato HH:00:00 en horas en punto"
        )
    if h.minute != 0 or h.second != 0:
        raise ValidationError(
            f"El campo '{campo}' es inválido",
            f"'{campo}' debe estar en hora en punto"
        )
    return h


def validar_intervalo_reserva(inicio: datetime, fin: datetime):
    """Valida duración 1-3h, horas en punto, dentro del horario del club, futuro."""
    if inicio >= fin:
        raise ValidationError(
            "El intervalo es inválido",
            "fecha_hora_inicio debe ser anterior a fecha_hora_fin"
        )
    if inicio.minute != 0 or inicio.second != 0 or inicio.microsecond != 0:
        raise ValidationError(
            "El intervalo es inválido",
            "fecha_hora_inicio debe estar en hora en punto"
        )
    if fin.minute != 0 or fin.second != 0 or fin.microsecond != 0:
        raise ValidationError(
            "El intervalo es inválido",
            "fecha_hora_fin debe estar en hora en punto"
        )

    duracion = (fin - inicio).total_seconds() / 3600
    if duracion < C.DURACION_MIN_HORAS or duracion > C.DURACION_MAX_HORAS:
        raise ValidationError(
            "La duración es inválida",
            "La reserva debe durar entre 1 y 3 horas completas"
        )

    if inicio.date() != fin.date():
        raise ValidationError(
            "El intervalo es inválido",
            "La reserva no puede atravesar la medianoche"
        )

    if inicio.hour < C.HORA_APERTURA or fin.hour > C.HORA_CIERRE:
        raise ValidationError(
            "El intervalo está fuera del horario del club",
            f"El club atiende de {C.HORA_APERTURA}:00 a {C.HORA_CIERRE}:00"
        )

    if inicio <= datetime.now():
        raise ValidationError(
            "La reserva no es futura",
            "El inicio de la reserva debe ser posterior al momento actual"
        )
    return int(duracion)


def validar_campos_permitidos(data: dict, permitidos: set):
    """Rechaza body con campos no declarados."""
    if not isinstance(data, dict):
        raise ValidationError("El cuerpo debe ser un objeto JSON")
    desconocidos = set(data.keys()) - permitidos
    if desconocidos:
        raise ValidationError(
            "El cuerpo contiene campos desconocidos",
            f"Campos no permitidos: {', '.join(sorted(desconocidos))}"
        )