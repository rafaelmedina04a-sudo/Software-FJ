# =====================================================================
# 5. RESERVA
# =====================================================================
class Estado(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(Entidad):
    _contador = count(1)

    def __init__(self, cliente: Cliente, servicio: Servicio, horas: float):
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        try:
            servicio.validar_parametros(horas)
        except ErrorSoftwareFJ as e:
            # encadenamiento de excepciones
            raise ReservaInvalidaError("Duración no válida para el servicio") from e
        self._cliente, self._servicio, self._horas = cliente, servicio, horas
        self._estado = Estado.PENDIENTE
        self._costo = None
        self._asignar_id()
        log.info("Reserva #%s creada: %s -> %s (%sh)", self.id,
                 cliente.nombre, servicio.nombre, horas)

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        if self._estado is not Estado.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva {self._estado.value}")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"'{self._servicio.nombre}' no está disponible")
        self._estado = Estado.CONFIRMADA
        log.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        if self._estado in (Estado.CANCELADA, Estado.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self._estado.value}")
        self._estado = Estado.CANCELADA
        log.info("Reserva #%s cancelada", self.id)

    def procesar(self, impuesto=0.19, descuento=0.0) -> float:
        """try/except/else/finally con encadenamiento de excepciones."""
        try:
            if self._estado is not Estado.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas confirmadas (estado: {self._estado.value})")
            costo = self._servicio.calcular_costo(self._horas, impuesto, descuento)
        except OperacionNoPermitidaError:
            raise
        except ErrorSoftwareFJ as e:
            raise ReservaInvalidaError(f"Fallo al procesar reserva #{self.id}") from e
        else:
            self._costo = costo
            self._estado = Estado.PROCESADA
            log.info("Reserva #%s procesada. Total $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            log.info("Intento de procesamiento de reserva #%s finalizado", self.id)

    def describir(self):
        costo = f"${self._costo:,.2f}" if self._costo is not None else "-"
        return (f"Reserva #{self.id} | {self._cliente.nombre} | {self._servicio.nombre} "
                f"| {self._horas}h | {self._estado.value} | Total: {costo}")
