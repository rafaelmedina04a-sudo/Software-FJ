
# =====================================================================
# 4. SERVICIO ABSTRACTO Y SERVICIOS ESPECIALIZADOS
# =====================================================================
class Service(Entidad):
    _contador = count(1)
    IVA_DEFECTO = 0.19
    TIPO = "Service"

    def __init__(self, nombre: str, tarifa_hora: float):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ParametroFaltanteError("A service name is required")
        if (not isinstance(tarifa_hora, (int, float)) or isinstance(tarifa_hora, bool)
                or not math.isfinite(tarifa_hora) or tarifa_hora <= 0):
            raise ServiceInvalidoError(f"Invalid hourly rate: {tarifa_hora!r}")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._available = True

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def available(self):
        return self._available

    def cambiar_disponibilidad(self, valor: bool):
        self._available = bool(valor)
        log.info("Service '%s' available=%s", self._nombre, self._available)

    @abstractmethod
    def validar_parametros(self, hours: float) -> None: ...

    @abstractmethod
    def calcular_costo_base(self, hours: float) -> float: ...

    @abstractmethod
    def detalle(self) -> str:
        """Details específico del tipo de servicio."""

    def calcular_costo(self, hours, *args, impuesto=None, descuento=None) -> float:
        """Sobrecarga simulada:
        calcular_costo(h)                            -> costo base
        calcular_costo(h, 0.19)                      -> con impuesto
        calcular_costo(h, 0.19, 0.10)                -> con impuesto y descuento
        calcular_costo(h, impuesto=.., descuento=..) -> parámetros keyword argumentss
        """
        if len(args) > 2:
            raise ServiceInvalidoError("Too many arguments passed to calculate_cost")
        if len(args) >= 1:
            impuesto = args[0]
        if len(args) == 2:
            descuento = args[1]
        impuesto = 0.0 if impuesto is None else impuesto
        descuento = 0.0 if descuento is None else descuento
        if (not isinstance(impuesto, (int, float)) or isinstance(impuesto, bool)
                or not math.isfinite(impuesto)
                or not isinstance(descuento, (int, float)) or isinstance(descuento, bool)
                or not math.isfinite(descuento)
                or not (0 <= impuesto <= 1) or not (0 <= descuento < 1)):
            raise CalculoInconsistenteError(
                f"Impuesto/descuento fuera de rango: {impuesto}, {descuento}")
        self.validar_parametros(hours)
        costo = self.calcular_costo_base(hours) * (1 - descuento) * (1 + impuesto)
        if costo <= 0:
            raise CalculoInconsistenteError(f"Costo no positivo: {costo}")
        return round(costo, 2)

    def calcular_costo_con_iva(self, hours) -> float:
        return self.calcular_costo(hours, self.IVA_DEFECTO)

    def describir(self):
        return (f"Service #{self.id} [{self.TIPO}] '{self._nombre}' "
                f"${self._tarifa_hora:,.0f}/h - {self.detalle()}")


class BookingSala(Service):
    TIPO = "Sala"

    def __init__(self, nombre, tarifa_hora, capacidad: int):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServiceInvalidoError(f"Invalid capacity: {capacidad!r}")
        self._capacidad = capacidad
        self._asignar_id()
        log.info("Service created: %s", self.describir())

    def validar_parametros(self, hours):
        if not isinstance(hours, (int, float)) or not 1 <= hours <= 12:
            raise ServiceInvalidoError(
                f"Sala: las hours deben estar entre 1 y 12 (recibido {hours!r})")

    def calcular_costo_base(self, hours):
        return self._tarifa_hora * hours

    def detalle(self):
        return f"capacidad {self._capacidad} personas"


class AlquilerEquipo(Service):
    TIPO = "Equipo"

    def __init__(self, nombre, tarifa_hora, cantidad: int, seguro: float = 0.0):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ServiceInvalidoError(f"Invalid quantity: {cantidad!r}")
        if (not isinstance(seguro, (int, float)) or isinstance(seguro, bool)
                or not math.isfinite(seguro) or seguro < 0):
            raise ServiceInvalidoError("Insurance fee cannot be negative")
        self._cantidad = cantidad
        self._seguro = float(seguro)
        self._asignar_id()
        log.info("Service created: %s", self.describir())

    def validar_parametros(self, hours):
        if not isinstance(hours, (int, float)) or not 1 <= hours <= 72:
            raise ServiceInvalidoError(
                f"Equipo: las hours deben estar entre 1 y 72 (recibido {hours!r})")

    def calcular_costo_base(self, hours):
        return self._tarifa_hora * hours * self._cantidad + self._seguro

    def detalle(self):
        return f"{self._cantidad} equipos, seguro ${self._seguro:,.0f}"


class Asesoria(Service):
    TIPO = "Asesoría"
    _RECARGO = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, nivel: str):
        super().__init__(nombre, tarifa_hora)
        nivel = nivel.strip().lower() if isinstance(nivel, str) else nivel
        if nivel not in self._RECARGO:
            raise ServiceInvalidoError(
                f"Invalid level: {nivel!r} (use junior, senior, or expert)")
        self._nivel = nivel
        self._asignar_id()
        log.info("Service created: %s", self.describir())

    def validar_parametros(self, hours):
        if not isinstance(hours, (int, float)) or not 0.5 <= hours <= 8:
            raise ServiceInvalidoError(
                f"Asesoría: las hours deben estar entre 0.5 y 8 (recibido {hours!r})")

    def calcular_costo_base(self, hours):
        return self._tarifa_hora * hours * self._RECARGO[self._nivel]

    def detalle(self):
        return f"nivel {self._nivel}"
