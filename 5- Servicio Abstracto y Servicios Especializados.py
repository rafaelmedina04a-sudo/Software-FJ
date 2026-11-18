# =====================================================================
# 4. SERVICIO ABSTRACTO Y SERVICIOS ESPECIALIZADO
# =====================================================================
class Servicio(Entidad):
    _contador = count(1)
    IVA_DEFECTO = 0.19
    TIPO = "Servicio"

    def __init__(self, nombre: str, tarifa_hora: float):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ParametroFaltanteError("El servicio requiere un nombre")
        if (not isinstance(tarifa_hora, (int, float)) or isinstance(tarifa_hora, bool)
                or tarifa_hora <= 0):
            raise ServicioInvalidoError(f"Tarifa inválida: {tarifa_hora!r}")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = True

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, valor: bool):
        self._disponible = bool(valor)
        log.info("Servicio '%s' disponible=%s", self._nombre, self._disponible)

    @abstractmethod
    def validar_parametros(self, horas: float) -> None: ...

    @abstractmethod
    def calcular_costo_base(self, horas: float) -> float: ...

    @abstractmethod
    def detalle(self) -> str:
        """Detalle específico del tipo de servicio."""

    def calcular_costo(self, horas, *args, impuesto=None, descuento=None) -> float:
        """Sobrecarga simulada:
        calcular_costo(h)                            -> costo base
        calcular_costo(h, 0.19)                      -> con impuesto
        calcular_costo(h, 0.19, 0.10)                -> con impuesto y descuento
        calcular_costo(h, impuesto=.., descuento=..) -> parámetros nombrados
        """
        if len(args) > 2:
            raise ServicioInvalidoError("Demasiados argumentos en calcular_costo")
        if len(args) >= 1:
            impuesto = args[0]
        if len(args) == 2:
            descuento = args[1]
        impuesto = 0.0 if impuesto is None else impuesto
        descuento = 0.0 if descuento is None else descuento
        if not (0 <= impuesto <= 1) or not (0 <= descuento < 1):
            raise CalculoInconsistenteError(
                f"Impuesto/descuento fuera de rango: {impuesto}, {descuento}")
        self.validar_parametros(horas)
        costo = self.calcular_costo_base(horas) * (1 - descuento) * (1 + impuesto)
        if costo <= 0:
            raise CalculoInconsistenteError(f"Costo no positivo: {costo}")
        return round(costo, 2)

    def calcular_costo_con_iva(self, horas) -> float:
        return self.calcular_costo(horas, self.IVA_DEFECTO)

    def describir(self):
        return (f"Servicio #{self.id} [{self.TIPO}] '{self._nombre}' "
                f"${self._tarifa_hora:,.0f}/h - {self.detalle()}")


class ReservaSala(Servicio):
    TIPO = "Sala"

    def __init__(self, nombre, tarifa_hora, capacidad: int):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad
        self._asignar_id()
        log.info("Servicio creado: %s", self.describir())

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 12:
            raise ServicioInvalidoError(
                f"Sala: las horas deben estar entre 1 y 12 (recibido {horas!r})")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas

    def detalle(self):
        return f"capacidad {self._capacidad} personas"


class AlquilerEquipo(Servicio):
    TIPO = "Equipo"

    def __init__(self, nombre, tarifa_hora, cantidad: int, seguro: float = 0.0):
        super().__init__(nombre, tarifa_hora)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ServicioInvalidoError(f"Cantidad inválida: {cantidad!r}")
        if seguro < 0:
            raise ServicioInvalidoError("El seguro no puede ser negativo")
        self._cantidad = cantidad
        self._seguro = float(seguro)
        self._asignar_id()
        log.info("Servicio creado: %s", self.describir())

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 1 <= horas <= 72:
            raise ServicioInvalidoError(
                f"Equipo: las horas deben estar entre 1 y 72 (recibido {horas!r})")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas * self._cantidad + self._seguro

    def detalle(self):
        return f"{self._cantidad} equipos, seguro ${self._seguro:,.0f}"


class Asesoria(Servicio):
    TIPO = "Asesoría"
    _RECARGO = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, nivel: str):
        super().__init__(nombre, tarifa_hora)
        nivel = nivel.strip().lower() if isinstance(nivel, str) else nivel
        if nivel not in self._RECARGO:
            raise ServicioInvalidoError(
                f"Nivel inválido: {nivel!r} (use junior, senior o experto)")
        self._nivel = nivel
        self._asignar_id()
        log.info("Servicio creado: %s", self.describir())

    def validar_parametros(self, horas):
        if not isinstance(horas, (int, float)) or not 0.5 <= horas <= 8:
            raise ServicioInvalidoError(
                f"Asesoría: las horas deben estar entre 0.5 y 8 (recibido {horas!r})")

    def calcular_costo_base(self, horas):
        return self._tarifa_hora * horas * self._RECARGO[self._nivel]

    def detalle(self):
        return f"nivel {self._nivel}"

