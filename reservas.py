from enum import Enum
from itertools import count
from configuracion import log
from excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
)
from entidades_clientes import Cliente
from servicios import Service


class EstadoReserva(Enum):
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva:
    _contador = count(1)

    def __init__(self, cliente: Cliente, servicio: Service, horas: float):
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se requiere un cliente válido para la reserva.")
        if not isinstance(servicio, Service):
            raise ReservaInvalidaError("Se requiere un servicio válido para la reserva.")
        
        try:
            horas_float = float(horas)
        except (ValueError, TypeError):
            raise ParametroFaltanteError("Las horas de la reserva deben ser un número válido.")
        
        if horas_float <= 0:
            raise ReservaInvalidaError("La duración en horas debe ser mayor a cero.")

        self._id = next(self._contador)
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas_float
        self._estado = EstadoReserva.CONFIRMADA
        self._costo = None

        log.info("Reserva #%d creada exitosamente para %s con servicio %s", self._id, cliente.nombre, servicio.nombre)

    @property
    def id(self) -> int:
        return self._id

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Service:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        if self._estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado {self._estado.value}")
        log.info("Reserva #%d confirmada.", self._id)

    def cancelar(self):
        if self._estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(f"La reserva #{self._id} ya se encuentra cancelada.")
        if self._estado == EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError(f"No se puede cancelar la reserva #{self._id} porque ya fue procesada.")
        
        self._estado = EstadoReserva.CANCELADA
        log.info("Reserva #%d cancelada.", self._id)

    def procesar(self, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        if self._estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError(f"No se puede procesar la reserva #{self._id} porque está cancelada.")
        
        try:
            # Calcula el costo usando la lógica de los servicios
            self._costo = self._servicio.calcular_costo(self._horas, impuesto=impuesto, descuento=descuento)
            if self._costo is None or self._costo < 0:
                raise CalculoInconsistenteError("El cálculo del costo de la reserva arrojó un valor inválido.")
            
            self._estado = EstadoReserva.PROCESADA
            log.info("Reserva #%d procesada. Costo total: $%.2f", self._id, self._costo)
            return self._costo
        except Exception as e:
            if isinstance(e, ErrorSoftwareFJ):
                raise
            raise CalculoInconsistenteError(f"Error al calcular el costo de la reserva: {e}")

    def describir(self) -> str:
        costo_str = f"${self._costo:,.2f}" if self._costo is not None else "Pendiente"
        return f"Reserva #{self._id} | Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre} | Horas: {self._horas} | Estado: {self._estado.value} | Total: {costo_str}"
