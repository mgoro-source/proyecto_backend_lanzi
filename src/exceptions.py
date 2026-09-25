class ApiError(Exception):
    """Base para errores de la API que se traducen a respuestas JSON."""
    status_code = 500
    code = "ERROR_INTERNO"

    def __init__(self, message: str, description: str = "", level: str = "error"):
        super().__init__(message)
        self.message = message
        self.description = description or message
        self.level = level

    def to_dict(self) -> dict:
        return {
            "errors": [{
                "code": self.code,
                "message": self.message,
                "level": self.level,
                "description": self.description,
            }]
        }


class ValidationError(ApiError):
    status_code = 400
    code = "ERROR_VALIDACION"


class NotFoundError(ApiError):
    status_code = 404
    code = "ERROR_NO_ENCONTRADO"


class ConflictError(ApiError):
    status_code = 409
    code = "ERROR_CONFLICTO"


class ConflictWithDataError(ConflictError):
    """Conflicto que además devuelve datos extra (ej: fechas en conflicto)."""
    def __init__(self, message: str, description: str = "", extra: dict = None): # type: ignore
        super().__init__(message, description)
        self.extra = extra or {}

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update(self.extra)
        return base