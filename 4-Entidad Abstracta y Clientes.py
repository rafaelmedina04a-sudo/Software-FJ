# =====================================================================
# 3. ENTIDAD ABSTRACTA Y CLIENTES
# =====================================================================
class Entidad(ABC):
    """Clase abstracta para cualquier entidad general del sistema.
    El id se asigna solo cuando la entidad se crea con éxito (sin saltos)."""

    def __init__(self):
        self._id = None

    def _asignar_id(self):
        self._id = next(self._contador)

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Descripción legible de la entidad."""

    def __str__(self):
        return self.describir()


class Cliente(Entidad):
    _contador = count(1)
    _RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

    def __init__(self, nombre: str, documento: str, email: str, telefono: str):
        super().__init__()
        try:
            self.nombre = nombre
            self.documento = documento
            self.email = email
            self.telefono = telefono
        except ClienteInvalidoError as e:
            log.error("Cliente no creado: %s", e)
            raise
        self._asignar_id()
        log.info("Cliente registrado: %s (doc %s)", self._nombre, self._documento)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, v):
        if not isinstance(v, str) or len(v.strip()) < 3 or any(c.isdigit() for c in v):
            raise ClienteInvalidoError(f"Nombre inválido: {v!r}")
        self._nombre = v.strip().title()

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, v):
        if not isinstance(v, str) or not v.isdigit() or not 6 <= len(v) <= 12:
            raise ClienteInvalidoError(f"Documento inválido (6 a 12 dígitos): {v!r}")
        self._documento = v

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, v):
        if not isinstance(v, str) or not self._RE_EMAIL.match(v):
            raise ClienteInvalidoError(f"Email inválido: {v!r}")
        self._email = v.lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, v):
        if not isinstance(v, str) or not v.isdigit() or len(v) != 10:
            raise ClienteInvalidoError(f"Teléfono inválido (10 dígitos): {v!r}")
        self._telefono = v

    def describir(self) -> str:
        return (f"Cliente #{self.id}: {self._nombre} | Doc {self._documento} | "
                f"{self._email} | Tel {self._telefono}")
