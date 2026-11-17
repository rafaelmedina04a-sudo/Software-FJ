"""Excepciones personalizadas del sistema Software FJ."""

class ErrorSoftwareFJ(Exception):

    """Excepción base del sistema."""


class ClienteInvalidoError(ErrorSoftwareFJ):

    """Datos de cliente inválidos."""


class ServicioInvalidoError(ErrorSoftwareFJ):

    """Parámetros de servicio inválidos."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):

    """El servicio no está disponible para reservar."""


class ParametroFaltanteError(ErrorSoftwareFJ):

    """Falta un parámetro obligatorio o es de tipo incorrecto."""


class ReservaInvalidaError(ErrorSoftwareFJ):

    """Datos o intento de reserva incorrecto."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):

    """Transición de estado u operación no permitida."""


class CalculoInconsistenteError(ErrorSoftwareFJ):

    """El cálculo de costos produjo un resultado inconsistente."""
