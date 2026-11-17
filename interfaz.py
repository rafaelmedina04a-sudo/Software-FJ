"""
Módulo: interfaz.py (Módulo 6 - Interfaz Gráfica)
Descripción: Interfaz de escritorio desarrollada con Tkinter para gestionar clientes,
servicios, reservas, ejecutar la simulación automática de 18 operaciones y visualizar
el archivo de logs en tiempo real.

Ejecución: python interfaz.py
"""

import tkinter as tk
from tkinter import messagebox, ttk

# Importación de excepciones personalizadas y configuración de logs (Módulo 1)
from excepciones import (
    BookingInvalidaError,
    ErrorSoftwareFJ,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    RUTA_LOG,
    log,
)

# Importación de la clase Customer (Módulo 2)
from entidades_clientes import Customer

# Importación de los servicios especializados (Módulo 3)
from servicios import AlquilerEquipo, Asesoria, BookingSala

# Importación de la clase Booking (Módulo 4)
from reservas import Booking

# Importación de la función de simulación automática (Módulo 5)
from simulacion import simulacion_demo


# Colores hexadecimales para la barra de estado inferior (éxito y error)
COLOR_OK = "#1b7f3b"
COLOR_ERR = "#b3261e"


def a_numero(texto: str, tipo: type, nombre: str):
    """Convierte una cadena de texto ingresada en un formulario a un tipo numérico.

    Parámetros:
        texto (str): Valor capturado desde una caja de texto (Entry).
        tipo (type): Tipo numérico destino (int o float).
        nombre (str): Nombre descriptivo del campo para mensajes de error.

    Retorna:
        int | float: El valor convertido al tipo numérico solicitado.

    Lanza:
        ParametroFaltanteError: Si el campo está vacío o no tiene formato numérico.
    """
    texto = texto.strip()
    if texto == "":
        raise ParametroFaltanteError(f"Missing field: {nombre}")
    try:
        # Reemplaza comas decimales por puntos antes de realizar la conversión
        return tipo(texto.replace(",", "."))
    except ValueError:
        raise ParametroFaltanteError(
            f"'{nombre}' must be a number ({tipo.__name__}), recibido {texto!r}"
        )


class App(tk.Tk):
    """Ventana principal de la aplicación de escritorio Software FJ.

    Administra las listas en memoria de clientes, servicios y reservas (sin base de datos),
    organizando la interacción en cinco pestañas mediante un widget Notebook.
    """

    # Opciones disponibles para el selector de tipo de servicio
    TIPOS = ("Room booking", "Equipment rental", "Professional consulting")

    def __init__(self):
        """Inicializa la ventana principal, estilos visuales, barra de estado y pestañas."""
        super().__init__()
        self.title("Software FJ - Gestión de Customers, Services y Bookings")
        self.geometry("1180x760")
        self.minsize(980, 650)

        # Listas en memoria que almacenan los objetos creados durante la sesión
        self.clientes, self.servicios, self.reservas = [], [], []

        # Configuración de estilos ttk para tablas, pestañas y botones
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TNotebook.Tab", padding=(16, 7), font=("Segoe UI", 10, "bold"))
        estilo.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 9, "bold"))
        estilo.configure("TButton", padding=(10, 6), font=("Segoe UI", 9))
        estilo.configure("TEntry", padding=5)
        estilo.configure("TCombobox", padding=5)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 15, "bold"))

        # Encabezado superior de la aplicación
        header = ttk.Frame(self, padding=(16, 12, 16, 4))
        header.pack(fill="x")
        ttk.Label(header, text="Software FJ", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Customer, services and booking management",
            font=("Segoe UI", 9),
            foreground="#64748b",
        ).pack(anchor="w", pady=(2, 0))

        # Barra de estado inferior para retroalimentación visual inmediata
        self.estado_var = tk.StringVar(value="Ready. Add a customer to get started.")
        self.estado_lbl = tk.Label(
            self,
            textvariable=self.estado_var,
            anchor="w",
            padx=12,
            pady=5,
            fg="white",
            bg="#444",
            font=("Segoe UI", 10),
        )
        self.estado_lbl.pack(side="bottom", fill="x")

        # Contenedor de pestañas principales
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=8)
        self._tab_clientes()
        self._tab_servicios()
        self._tab_reservas()
        self._tab_simulacion()
        self._tab_log()

        # Actualiza el visor de logs automáticamente cada vez que el usuario cambia de pestaña
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refrescar_log())
        log.info("=== Sesión gráfica iniciada ===")
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ---------------- utilidades ----------------
    def _cerrar(self):
        """Registra el cierre de la sesión gráfica en el log y destruye la ventana."""
        log.info("=== Sesión gráfica finalizada ===")
        self.destroy()

    def estado(self, texto: str, ok: bool = True):
        """Actualiza el mensaje y color de fondo de la barra de estado inferior."""
        self.estado_var.set(texto)
        self.estado_lbl.config(bg=COLOR_OK if ok else COLOR_ERR)

    def ejecutar(self, titulo: str, accion) -> bool:
        """Ejecuta una acción de interfaz bajo un bloque completo try/except/else/finally.

        Garantiza que cualquier error controlado o inesperado sea capturado, mostrado al
        usuario y registrado en el archivo de logs sin detener la ejecución del programa.
        """
        try:
            mensaje = accion()
        except ErrorSoftwareFJ as e:
            # Captura excepciones propias del dominio e incluye su causa encadenada si existe
            causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
            log.error("'%s' falló: %s%s", titulo, e, causa)
            self.estado(f"✖ {titulo}: {e}{causa}", ok=False)
            messagebox.showerror("Handled error", f"{e}{causa}", parent=self)
            return False
        except Exception as e:
            # Captura cualquier error inesperado para mantener la estabilidad del sistema
            log.critical("'%s' error inesperado: %r", titulo, e, exc_info=True)
            self.estado(f"✖ Unexpected error in '{titulo}': {e!r}", ok=False)
            messagebox.showerror("Unexpected error (handled)", repr(e), parent=self)
            return False
        else:
            # Se ejecuta únicamente si la acción culminó sin lanzar excepciones
            log.info("'%s' exitosa", titulo)
            self.estado(f"✔ {mensaje}", ok=True)
            return True
        finally:
            # Se ejecuta siempre para registrar el fin de la operación y refrescar tablas
            log.info("'%s' terminada", titulo)
            self.refrescar()

    def _campo(self, padre, etiqueta: str, fila: int, ancho: int = 28, **kw) -> ttk.Entry:
        """Crea y posiciona un par etiqueta + caja de texto (Entry) en una cuadrícula."""
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=6, pady=4)
        e = ttk.Entry(padre, width=ancho, **kw)
        e.grid(row=fila, column=1, sticky="w", padx=6, pady=4)
        return e

    def _tabla(self, padre, columnas: tuple, anchos: tuple) -> ttk.Treeview:
        """Construye un componente Treeview con encabezados y barra de desplazamiento vertical."""
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True, padx=8, pady=6)
        tv = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse")
        for c, a in zip(columnas, anchos):
            tv.heading(c, text=c)
            tv.column(c, width=a, anchor="w")
        sb = ttk.Scrollbar(marco, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tv

    # ---------------- pestaña clientes ----------------
    def _tab_clientes(self):
        """Construye la pestaña de registro y listado de clientes."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Customers  ")
        form = ttk.LabelFrame(f, text="Add Customer")
        form.pack(fill="x", padx=8, pady=8)

        self.c_nombre = self._campo(form, "Full name", 0)
        self.c_doc = self._campo(form, "Document number (6–12 digits)", 1)
        self.c_email = self._campo(form, "Email", 2)
        self.c_tel = self._campo(form, "Phone number (10 digits)", 3)
        ttk.Button(form, text="Add Customer", command=self.registrar_cliente).grid(
            row=4, column=1, sticky="w", padx=6, pady=8
        )

        self.tv_clientes = self._tabla(
            f, ("#", "Name", "Document", "Email", "Phone"), (50, 230, 130, 260, 130)
        )

    def registrar_cliente(self):
        """Toma los datos del formulario, instancia un objeto Customer y lo guarda en memoria."""
        def accion():
            c = Customer(
                self.c_nombre.get(),
                self.c_doc.get().strip(),
                self.c_email.get().strip(),
                self.c_tel.get().strip(),
            )
            self.clientes.append(c)
            # Limpia los campos del formulario tras un registro exitoso
            for e in (self.c_nombre, self.c_doc, self.c_email, self.c_tel):
                e.delete(0, "end")
            return f"Customer registrado: {c.nombre}"

        self.ejecutar("Add Customer", accion)

    # ---------------- pestaña servicios ----------------
    def _tab_servicios(self):
        """Construye la pestaña de creación, listado y disponibilidad de servicios."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Services  ")
        form = ttk.LabelFrame(f, text="Create Service")
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Service type").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.s_tipo = ttk.Combobox(form, values=self.TIPOS, state="readonly", width=26)
        self.s_tipo.current(0)
        self.s_tipo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self.s_tipo.bind("<<ComboboxSelected>>", lambda e: self._ajustar_form_servicio())

        self.s_nombre = self._campo(form, "Service name", 1)
        self.s_tarifa = self._campo(form, "Hourly rate ($)", 2)

        # Campos dinámicos que cambian según el tipo de servicio elegido
        self.s_lbl1 = ttk.Label(form)
        self.s_lbl1.grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.s_ex1 = ttk.Entry(form, width=28)
        self.s_ex1.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        self.s_lbl2 = ttk.Label(form)
        self.s_lbl2.grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.s_ex2 = ttk.Entry(form, width=28)
        self.s_ex2.grid(row=4, column=1, sticky="w", padx=6, pady=4)

        botones = ttk.Frame(form)
        botones.grid(row=5, column=1, sticky="w", padx=6, pady=8)
        ttk.Button(botones, text="Create Service", command=self.crear_servicio).pack(side="left")
        ttk.Button(
            botones,
            text="Toggle selected service availability",
            command=self.cambiar_disponibilidad,
        ).pack(side="left", padx=10)

        self._ajustar_form_servicio()
        self.tv_servicios = self._tabla(
            f,
            ("#", "Type", "Name", "Tarifa/h", "Details", "Available"),
            (50, 90, 220, 110, 280, 100),
        )

    def _ajustar_form_servicio(self):
        """Adapta las etiquetas y estado de los campos extra según el servicio seleccionado."""
        i = self.s_tipo.current()
        if i == 0:
            # Reserva de sala: solo requiere capacidad de personas
            self.s_lbl1.config(text="Capacity (people)")
            self.s_lbl2.config(text="")
            self.s_ex2.delete(0, "end")
            self.s_ex2.config(state="disabled")
        elif i == 1:
            # Alquiler de equipo: requiere cantidad y un seguro opcional
            self.s_lbl1.config(text="Number of items")
            self.s_lbl2.config(text="Insurance fee $ (optional)")
            self.s_ex2.config(state="normal")
        else:
            # Asesoría: requiere el nivel del consultor
            self.s_lbl1.config(text="Level (junior/senior/expert)")
            self.s_lbl2.config(text="")
            self.s_ex2.delete(0, "end")
            self.s_ex2.config(state="disabled")

    def crear_servicio(self):
        """Instancia el servicio especializado correspondiente y lo agrega a la lista."""
        def accion():
            i = self.s_tipo.current()
            nombre = self.s_nombre.get()
            tarifa = a_numero(self.s_tarifa.get(), float, "Tarifa por hora")
            if i == 0:
                s = BookingSala(nombre, tarifa, a_numero(self.s_ex1.get(), int, "Capacidad"))
            elif i == 1:
                cant = a_numero(self.s_ex1.get(), int, "Cantidad")
                seguro = (
                    a_numero(self.s_ex2.get(), float, "Seguro")
                    if self.s_ex2.get().strip()
                    else 0.0
                )
                s = AlquilerEquipo(nombre, tarifa, cant, seguro)
            else:
                s = Asesoria(nombre, tarifa, self.s_ex1.get())
            self.servicios.append(s)
            for e in (self.s_nombre, self.s_tarifa, self.s_ex1, self.s_ex2):
                e.delete(0, "end")
            return f"Service creado: {s.nombre}"

        self.ejecutar("Create Service", accion)

    def cambiar_disponibilidad(self):
        """Alterna el estado de disponibilidad del servicio seleccionado en la tabla."""
        def accion():
            s = self._seleccionado(self.tv_servicios, self.servicios, "a service")
            s.cambiar_disponibilidad(not s.available)
            return f"'{s.nombre}' is now {'available' if s.available else 'No available'}"

        self.ejecutar("Cambiar disponibilidad", accion)

    # ---------------- pestaña reservas ----------------
    def _tab_reservas(self):
        """Construye la pestaña de creación, cotización y gestión de estados de reservas."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Bookings  ")
        form = ttk.LabelFrame(f, text="Create Booking")
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Customer").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.r_cli = ttk.Combobox(form, state="readonly", width=40)
        self.r_cli.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(form, text="Service").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.r_srv = ttk.Combobox(form, state="readonly", width=40)
        self.r_srv.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        self.r_hours = self._campo(form, "Duration (hours)", 2, ancho=12)
        ttk.Button(form, text="Create Booking", command=self.crear_reserva).grid(
            row=3, column=1, sticky="w", padx=6, pady=8
        )

        # Panel de acciones sobre reservas existentes y parámetros de impuesto/descuento
        acc = ttk.LabelFrame(f, text="Actions for selected booking")
        acc.pack(fill="x", padx=8, pady=2)
        ttk.Label(acc, text="Tax %").grid(row=0, column=0, padx=6, pady=6)
        self.r_imp = ttk.Entry(acc, width=7)
        self.r_imp.insert(0, "19")
        self.r_imp.grid(row=0, column=1, padx=2)
        ttk.Label(acc, text="Discount %").grid(row=0, column=2, padx=6)
        self.r_desc = ttk.Entry(acc, width=7)
        self.r_desc.insert(0, "0")
        self.r_desc.grid(row=0, column=3, padx=2)

        ttk.Button(acc, text="Confirm", command=self.confirmar_reserva).grid(
            row=0, column=4, padx=(18, 4)
        )
        ttk.Button(
            acc, text="Process (calculate total)", command=self.procesar_reserva
        ).grid(row=0, column=5, padx=4)
        ttk.Button(acc, text="Cancel", command=self.cancelar_reserva).grid(row=0, column=6, padx=4)
        ttk.Button(acc, text="Get Quote", command=self.cotizar).grid(row=0, column=7, padx=(18, 4))

        self.tv_reservas = self._tabla(
            f, ("#", "Customer", "Service", "Horas", "Status", "Total"), (50, 210, 210, 80, 120, 140)
        )
        # Colores visuales según el estado de la reserva
        self.tv_reservas.tag_configure("Confirmed", foreground="#0b57d0")
        self.tv_reservas.tag_configure("Processed", foreground=COLOR_OK)
        self.tv_reservas.tag_configure("Cancelled", foreground=COLOR_ERR)

    def _seleccionado(self, tv: ttk.Treeview, lista: list, que: str):
        """Obtiene el objeto correspondiente a la fila seleccionada en un Treeview."""
        sel = tv.selection()
        if not sel:
            raise OperacionNoPermitidaError(f"Please select {que} de la tabla")
        n = int(sel[0])
        for item in lista:
            if item.id == n:
                return item
        raise OperacionNoPermitidaError("The selected item no longer exists")

    def crear_reserva(self):
        """Crea una nueva reserva en estado pendiente vinculando cliente, servicio y horas."""
        def accion():
            ic, is_ = self.r_cli.current(), self.r_srv.current()
            if ic < 0:
                raise BookingInvalidaError("Please select a customer")
            if is_ < 0:
                raise BookingInvalidaError("Please select a service")
            hours = a_numero(self.r_hours.get(), float, "Duration (hours)")
            r = Booking(self.clientes[ic], self.servicios[is_], hours)
            self.reservas.append(r)
            self.r_hours.delete(0, "end")
            return f"Booking #{r.id} creada (estado Pending)"

        self.ejecutar("Create Booking", accion)

    def confirmar_reserva(self):
        """Cambia el estado de la reserva seleccionada a Confirmada."""
        def accion():
            r = self._seleccionado(self.tv_reservas, self.reservas, "a booking")
            r.confirmar()
            return f"Booking #{r.id} confirmada"

        self.ejecutar("Confirm reserva", accion)

    def cancelar_reserva(self):
        """Cambia el estado de la reserva seleccionada a Cancelada."""
        def accion():
            r = self._seleccionado(self.tv_reservas, self.reservas, "a booking")
            r.cancelar()
            return f"Booking #{r.id} cancelada"

        self.ejecutar("Cancel reserva", accion)

    def procesar_reserva(self):
        """Procesa una reserva confirmada calculando su total con impuestos y descuentos."""
        def accion():
            r = self._seleccionado(self.tv_reservas, self.reservas, "a booking")
            imp = a_numero(self.r_imp.get() or "0", float, "Tax %") / 100
            desc = a_numero(self.r_desc.get() or "0", float, "Discount %") / 100
            total = r.procesar(imp, desc)
            return f"Booking #{r.id} procesada. Total: ${total:,.2f}"

        self.ejecutar("Procesar reserva", accion)

    def cotizar(self):
        """Muestra una ventana emergente con las tres variantes de cálculo de costo del servicio."""
        def accion():
            i = self.r_srv.current()
            if i < 0:
                raise BookingInvalidaError("Please select a service en el formulario de reserva")
            s = self.servicios[i]
            hours = a_numero(self.r_hours.get(), float, "Duration (hours)")
            imp = a_numero(self.r_imp.get() or "0", float, "Tax %") / 100
            desc = a_numero(self.r_desc.get() or "0", float, "Discount %") / 100

            # Uso de las variantes de cálculo de costos
            base = s.calcular_costo(hours)
            iva = s.calcular_costo_con_iva(hours)
            final = s.calcular_costo(hours, impuesto=imp, descuento=desc)

            messagebox.showinfo(
                "Quote",
                f"{s.nombre} - {hours} h\n\nBase cost: ${base:,.2f}\n"
                f"With 19% tax: ${iva:,.2f}\nWith your values: ${final:,.2f}",
                parent=self,
            )
            return f"Quote de '{s.nombre}' calculada"

        self.ejecutar("Get Quote", accion)

    # ---------------- pestaña simulación ----------------
    def _tab_simulacion(self):
        """Construye la pestaña dedicada a ejecutar y visualizar la simulación automática."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Simulation  ")
        barra = ttk.Frame(f)
        barra.pack(fill="x", padx=8, pady=8)

        ttk.Button(
            barra,
            text="▶ Run simulation (18 operations)",
            command=self.ejecutar_simulacion,
        ).pack(side="left")
        ttk.Button(
            barra, text="Clear", command=lambda: self._set_texto(self.txt_sim, "")
        ).pack(side="left", padx=8)

        self.txt_sim = tk.Text(f, wrap="word", font=("Consolas", 10), state="disabled")
        self.txt_sim.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.txt_sim.tag_configure("err", foreground=COLOR_ERR)
        self.txt_sim.tag_configure("ok", foreground=COLOR_OK)

    def _set_texto(self, widget: tk.Text, texto: str):
        """Reemplaza el contenido de un widget Text de solo lectura de forma segura."""
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)
        widget.config(state="disabled")

    def ejecutar_simulacion(self):
        """Lanza las 18 operaciones de prueba y muestra sus resultados en tiempo real."""
        self._set_texto(self.txt_sim, "")

        def emit(linea: str):
            """Callback que recibe cada línea de salida de la simulación y la colorea."""
            self.txt_sim.config(state="normal")
            tag = "err" if "✖" in linea else ("ok" if "✔" in linea else "")
            self.txt_sim.insert("end", linea + "\n", tag)
            self.txt_sim.config(state="disabled")
            self.txt_sim.see("end")
            self.update_idletasks()

        try:
            simulacion_demo(emit)
            self.estado("✔ Simulation terminada: el sistema siguió estable ante todos los errores")
        except Exception as e:
            log.critical("Simulation failed: %r", e, exc_info=True)
            self.estado(f"✖ Simulation failed: {e!r}", ok=False)

    # ---------------- pestaña log ----------------
    def _tab_log(self):
        """Construye la pestaña de consulta del archivo físico de logs del sistema."""
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Activity Log  ")
        barra = ttk.Frame(f)
        barra.pack(fill="x", padx=8, pady=8)

        ttk.Button(barra, text="Refresh", command=self.refrescar_log).pack(side="left")
        ttk.Label(barra, text=f"File: {RUTA_LOG}").pack(side="left", padx=12)

        self.txt_log = tk.Text(f, wrap="none", font=("Consolas", 9), state="disabled")
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refrescar_log(self):
        """Lee las últimas 300 líneas del archivo software_fj.log y las muestra en pantalla."""
        try:
            lineas = RUTA_LOG.read_text(encoding="utf-8").splitlines()[-300:]
            self._set_texto(self.txt_log, "\n".join(lineas))
            self.txt_log.see("end")
        except OSError as e:
            log.error("Could not read log file: %s", e)

    # ---------------- refresco de tablas y listas ----------------
    def refrescar(self):
        """Sincroniza el contenido de las tablas y listas desplegables con la memoria."""
        # Conserva la fila seleccionada de cada tabla antes de limpiarla
        previas = {
            tv: tv.selection()
            for tv in (self.tv_clientes, self.tv_servicios, self.tv_reservas)
        }
        for tv in previas:
            tv.delete(*tv.get_children())

        for c in self.clientes:
            self.tv_clientes.insert(
                "",
                "end",
                iid=str(c.id),
                values=(c.id, c.nombre, c.documento, c.email, c.telefono),
            )
        for s in self.servicios:
            self.tv_servicios.insert(
                "",
                "end",
                iid=str(s.id),
                values=(
                    s.id,
                    s.TIPO,
                    s.nombre,
                    f"${s.tarifa_hora:,.0f}",
                    s.detalle(),
                    "Yes" if s.available else "No",
                ),
            )
        for r in self.reservas:
            total = f"${r.costo:,.2f}" if r.costo is not None else "-"
            self.tv_reservas.insert(
                "",
                "end",
                iid=str(r.id),
                tags=(r.estado.value,),
                values=(
                    r.id,
                    r.cliente.nombre,
                    r.servicio.nombre,
                    r.horas,
                    r.estado.value,
                    total,
                ),
            )

        # Restaura la selección previa si el registro aún existe
        for tv, sel in previas.items():
            if sel and tv.exists(sel[0]):
                tv.selection_set(sel[0])

        # Actualiza las opciones de los desplegables en la pestaña de reservas
        self.r_cli["values"] = [f"{c.id} - {c.nombre}" for c in self.clientes]
        self.r_srv["values"] = [f"{s.id} - {s.nombre} ({s.TIPO})" for s in self.servicios]


def main():
    """Punto de entrada principal de la aplicación gráfica."""
    try:
        app = App()
    except tk.TclError as e:
        log.critical("No se pudo abrir la ventana: %s", e)
        print("Could not open the graphical interface (is a display available?):", e)
        return
    app.mainloop()


if __name__ == "__main__":
    main()
