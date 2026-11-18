# =====================================================================
# 7. INTERFAZ GRÁFICA 
# =====================================================================
COLOR_OK, COLOR_ERR = "#1b7f3b", "#b3261e"


def a_numero(texto, tipo, nombre):
    texto = texto.strip()
    if texto == "":
        raise ParametroFaltanteError(f"Falta el campo: {nombre}")
    try:
        return tipo(texto.replace(",", "."))
    except ValueError:
        raise ParametroFaltanteError(f"'{nombre}' debe ser un número ({tipo.__name__}), recibido {texto!r}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software FJ - Gestión de Clientes, Servicios y Reservas")
        self.geometry("1020x680")
        self.minsize(900, 600)
        self.clientes, self.servicios, self.reservas = [], [], []

        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TNotebook.Tab", padding=(16, 7), font=("Segoe UI", 10, "bold"))
        estilo.configure("Treeview", rowheight=24)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 15, "bold"))

        ttk.Label(self, text="Software FJ", style="Titulo.TLabel").pack(anchor="w", padx=14, pady=(10, 0))
        self.estado_var = tk.StringVar(value="Listo. Registra un cliente para comenzar.")
        self.estado_lbl = tk.Label(self, textvariable=self.estado_var, anchor="w", padx=12,
                                   pady=5, fg="white", bg="#444", font=("Segoe UI", 10))
        self.estado_lbl.pack(side="bottom", fill="x")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=8)
        self._tab_clientes()
        self._tab_servicios()
        self._tab_reservas()
        self._tab_simulacion()
        self._tab_log()
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refrescar_log())
        log.info("=== Sesión gráfica iniciada ===")
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ---------------- utilidades ----------------
    def _cerrar(self):
        log.info("=== Sesión gráfica finalizada ===")
        self.destroy()

    def estado(self, texto, ok=True):
        self.estado_var.set(texto)
        self.estado_lbl.config(bg=COLOR_OK if ok else COLOR_ERR)

    def ejecutar(self, titulo, accion):
        """Ejecuta una acción; todo error se registra, se muestra y la app sigue activa."""
        try:
            mensaje = accion()
        except ErrorSoftwareFJ as e:
            causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
            log.error("'%s' falló: %s%s", titulo, e, causa)
            self.estado(f"✖ {titulo}: {e}{causa}", ok=False)
            messagebox.showerror("Error controlado", f"{e}{causa}", parent=self)
            return False
        except Exception as e:  # error inesperado: el sistema no se detiene
            log.critical("'%s' error inesperado: %r", titulo, e, exc_info=True)
            self.estado(f"✖ Error inesperado en '{titulo}': {e!r}", ok=False)
            messagebox.showerror("Error inesperado (controlado)", repr(e), parent=self)
            return False
        else:
            log.info("'%s' exitosa", titulo)
            self.estado(f"✔ {mensaje}", ok=True)
            return True
        finally:
            log.info("'%s' terminada", titulo)
            self.refrescar()

    def _campo(self, padre, etiqueta, fila, ancho=28, **kw):
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=6, pady=4)
        e = ttk.Entry(padre, width=ancho, **kw)
        e.grid(row=fila, column=1, sticky="w", padx=6, pady=4)
        return e

    def _tabla(self, padre, columnas, anchos):
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
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Clientes  ")
        form = ttk.LabelFrame(f, text="Registrar cliente")
        form.pack(fill="x", padx=8, pady=8)
        self.c_nombre = self._campo(form, "Nombre completo", 0)
        self.c_doc = self._campo(form, "Documento (6-12 dígitos)", 1)
        self.c_email = self._campo(form, "Email", 2)
        self.c_tel = self._campo(form, "Teléfono (10 dígitos)", 3)
        ttk.Button(form, text="Registrar cliente", command=self.registrar_cliente).grid(
            row=4, column=1, sticky="w", padx=6, pady=8)
        self.tv_clientes = self._tabla(
            f, ("#", "Nombre", "Documento", "Email", "Teléfono"), (50, 230, 130, 260, 130))

    def registrar_cliente(self):
        def accion():
            c = Cliente(self.c_nombre.get(), self.c_doc.get().strip(),
                        self.c_email.get().strip(), self.c_tel.get().strip())
            self.clientes.append(c)
            for e in (self.c_nombre, self.c_doc, self.c_email, self.c_tel):
                e.delete(0, "end")
            return f"Cliente registrado: {c.nombre}"
        self.ejecutar("Registrar cliente", accion)

    # ---------------- pestaña servicios ----------------
    TIPOS = ("Reserva de sala", "Alquiler de equipo", "Asesoría especializada")

    def _tab_servicios(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Servicios  ")
        form = ttk.LabelFrame(f, text="Crear servicio")
        form.pack(fill="x", padx=8, pady=8)
        ttk.Label(form, text="Tipo de servicio").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.s_tipo = ttk.Combobox(form, values=self.TIPOS, state="readonly", width=26)
        self.s_tipo.current(0)
        self.s_tipo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self.s_tipo.bind("<<ComboboxSelected>>", lambda e: self._ajustar_form_servicio())
        self.s_nombre = self._campo(form, "Nombre del servicio", 1)
        self.s_tarifa = self._campo(form, "Tarifa por hora ($)", 2)
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
        ttk.Button(botones, text="Crear servicio", command=self.crear_servicio).pack(side="left")
        ttk.Button(botones, text="Cambiar disponibilidad del seleccionado",
                   command=self.cambiar_disponibilidad).pack(side="left", padx=10)
        self._ajustar_form_servicio()
        self.tv_servicios = self._tabla(
            f, ("#", "Tipo", "Nombre", "Tarifa/h", "Detalle", "Disponible"), (50, 90, 220, 110, 280, 100))

    def _ajustar_form_servicio(self):
        i = self.s_tipo.current()
        if i == 0:
            self.s_lbl1.config(text="Capacidad (personas)")
            self.s_lbl2.config(text="")
            self.s_ex2.delete(0, "end")
            self.s_ex2.config(state="disabled")
        elif i == 1:
            self.s_lbl1.config(text="Cantidad de equipos")
            self.s_lbl2.config(text="Seguro $ (opcional)")
            self.s_ex2.config(state="normal")
        else:
            self.s_lbl1.config(text="Nivel (junior/senior/experto)")
            self.s_lbl2.config(text="")
            self.s_ex2.delete(0, "end")
            self.s_ex2.config(state="disabled")

    def crear_servicio(self):
        def accion():
            i = self.s_tipo.current()
            nombre = self.s_nombre.get()
            tarifa = a_numero(self.s_tarifa.get(), float, "Tarifa por hora")
            if i == 0:
                s = ReservaSala(nombre, tarifa, a_numero(self.s_ex1.get(), int, "Capacidad"))
            elif i == 1:
                cant = a_numero(self.s_ex1.get(), int, "Cantidad")
                seguro = a_numero(self.s_ex2.get(), float, "Seguro") if self.s_ex2.get().strip() else 0.0
                s = AlquilerEquipo(nombre, tarifa, cant, seguro)
            else:
                s = Asesoria(nombre, tarifa, self.s_ex1.get())
            self.servicios.append(s)
            for e in (self.s_nombre, self.s_tarifa, self.s_ex1, self.s_ex2):
                e.delete(0, "end")
            return f"Servicio creado: {s.nombre}"
        self.ejecutar("Crear servicio", accion)

    def cambiar_disponibilidad(self):
        def accion():
            s = self._seleccionado(self.tv_servicios, self.servicios, "un servicio")
            s.cambiar_disponibilidad(not s.disponible)
            return f"'{s.nombre}' ahora {'disponible' if s.disponible else 'NO disponible'}"
        self.ejecutar("Cambiar disponibilidad", accion)

    # ---------------- pestaña reservas ----------------
    def _tab_reservas(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Reservas  ")
        form = ttk.LabelFrame(f, text="Crear reserva")
        form.pack(fill="x", padx=8, pady=8)
        ttk.Label(form, text="Cliente").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.r_cli = ttk.Combobox(form, state="readonly", width=40)
        self.r_cli.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(form, text="Servicio").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.r_srv = ttk.Combobox(form, state="readonly", width=40)
        self.r_srv.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        self.r_horas = self._campo(form, "Duración (horas)", 2, ancho=12)
        ttk.Button(form, text="Crear reserva", command=self.crear_reserva).grid(
            row=3, column=1, sticky="w", padx=6, pady=8)

        acc = ttk.LabelFrame(f, text="Acciones sobre la reserva seleccionada")
        acc.pack(fill="x", padx=8, pady=2)
        ttk.Label(acc, text="Impuesto %").grid(row=0, column=0, padx=6, pady=6)
        self.r_imp = ttk.Entry(acc, width=7)
        self.r_imp.insert(0, "19")
        self.r_imp.grid(row=0, column=1, padx=2)
        ttk.Label(acc, text="Descuento %").grid(row=0, column=2, padx=6)
        self.r_desc = ttk.Entry(acc, width=7)
        self.r_desc.insert(0, "0")
        self.r_desc.grid(row=0, column=3, padx=2)
        ttk.Button(acc, text="Confirmar", command=self.confirmar_reserva).grid(row=0, column=4, padx=(18, 4))
        ttk.Button(acc, text="Procesar (calcular total)", command=self.procesar_reserva).grid(row=0, column=5, padx=4)
        ttk.Button(acc, text="Cancelar", command=self.cancelar_reserva).grid(row=0, column=6, padx=4)
        ttk.Button(acc, text="Cotizar servicio", command=self.cotizar).grid(row=0, column=7, padx=(18, 4))

        self.tv_reservas = self._tabla(
            f, ("#", "Cliente", "Servicio", "Horas", "Estado", "Total"), (50, 210, 210, 80, 120, 140))
        self.tv_reservas.tag_configure("Confirmada", foreground="#0b57d0")
        self.tv_reservas.tag_configure("Procesada", foreground=COLOR_OK)
        self.tv_reservas.tag_configure("Cancelada", foreground=COLOR_ERR)

    def _seleccionado(self, tv, lista, que):
        sel = tv.selection()
        if not sel:
            raise OperacionNoPermitidaError(f"Seleccione {que} de la tabla")
        n = int(sel[0])
        for item in lista:
            if item.id == n:
                return item
        raise OperacionNoPermitidaError("El elemento seleccionado ya no existe")

    def crear_reserva(self):
        def accion():
            ic, is_ = self.r_cli.current(), self.r_srv.current()
            if ic < 0:
                raise ReservaInvalidaError("Seleccione un cliente")
            if is_ < 0:
                raise ReservaInvalidaError("Seleccione un servicio")
            horas = a_numero(self.r_horas.get(), float, "Duración (horas)")
            r = Reserva(self.clientes[ic], self.servicios[is_], horas)
            self.reservas.append(r)
            self.r_horas.delete(0, "end")
            return f"Reserva #{r.id} creada (estado Pendiente)"
        self.ejecutar("Crear reserva", accion)

    def confirmar_reserva(self):
        def accion():
            r = self._seleccionado(self.tv_reservas, self.reservas, "una reserva")
            r.confirmar()
            return f"Reserva #{r.id} confirmada"
        self.ejecutar("Confirmar reserva", accion)

    def cancelar_reserva(self):
        def accion():
            r = self._seleccionado(self.tv_reservas, self.reservas, "una reserva")
            r.cancelar()
            return f"Reserva #{r.id} cancelada"
        self.ejecutar("Cancelar reserva", accion)

    def procesar_reserva(self):
        def accion():
            r = self._seleccionado(self.tv_reservas, self.reservas, "una reserva")
            imp = a_numero(self.r_imp.get() or "0", float, "Impuesto %") / 100
            desc = a_numero(self.r_desc.get() or "0", float, "Descuento %") / 100
            total = r.procesar(imp, desc)
            return f"Reserva #{r.id} procesada. Total: ${total:,.2f}"
        self.ejecutar("Procesar reserva", accion)

    def cotizar(self):
        def accion():
            i = self.r_srv.current()
            if i < 0:
                raise ReservaInvalidaError("Seleccione un servicio en el formulario de reserva")
            s = self.servicios[i]
            horas = a_numero(self.r_horas.get(), float, "Duración (horas)")
            imp = a_numero(self.r_imp.get() or "0", float, "Impuesto %") / 100
            desc = a_numero(self.r_desc.get() or "0", float, "Descuento %") / 100
            base = s.calcular_costo(horas)
            iva = s.calcular_costo_con_iva(horas)
            final = s.calcular_costo(horas, impuesto=imp, descuento=desc)
            messagebox.showinfo(
                "Cotización", f"{s.nombre} - {horas} h\n\nCosto base: ${base:,.2f}\n"
                f"Con IVA 19%: ${iva:,.2f}\nCon tus valores: ${final:,.2f}", parent=self)
            return f"Cotización de '{s.nombre}' calculada"
        self.ejecutar("Cotizar servicio", accion)

    # ---------------- pestaña simulación ----------------
    def _tab_simulacion(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Simulación  ")
        barra = ttk.Frame(f)
        barra.pack(fill="x", padx=8, pady=8)
        ttk.Button(barra, text="▶ Ejecutar simulación (18 operaciones)",
                   command=self.ejecutar_simulacion).pack(side="left")
        ttk.Button(barra, text="Limpiar", command=lambda: self._set_texto(self.txt_sim, "")).pack(side="left", padx=8)
        self.txt_sim = tk.Text(f, wrap="word", font=("Consolas", 10), state="disabled")
        self.txt_sim.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.txt_sim.tag_configure("err", foreground=COLOR_ERR)
        self.txt_sim.tag_configure("ok", foreground=COLOR_OK)

    def _set_texto(self, widget, texto):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)
        widget.config(state="disabled")

    def ejecutar_simulacion(self):
        self._set_texto(self.txt_sim, "")

        def emit(linea):
            self.txt_sim.config(state="normal")
            tag = "err" if "✖" in linea else ("ok" if "✔" in linea else "")
            self.txt_sim.insert("end", linea + "\n", tag)
            self.txt_sim.config(state="disabled")
            self.txt_sim.see("end")
            self.update_idletasks()
        try:
            simulacion_demo(emit)
            self.estado("✔ Simulación terminada: el sistema siguió estable ante todos los errores")
        except Exception as e:
            log.critical("Fallo en simulación: %r", e, exc_info=True)
            self.estado(f"✖ Fallo en simulación: {e!r}", ok=False)

    # ---------------- pestaña log ----------------
    def _tab_log(self):
        f = ttk.Frame(self.nb)
        self.nb.add(f, text="  Log de eventos  ")
        barra = ttk.Frame(f)
        barra.pack(fill="x", padx=8, pady=8)
        ttk.Button(barra, text="Actualizar", command=self.refrescar_log).pack(side="left")
        ttk.Label(barra, text=f"Archivo: {RUTA_LOG}").pack(side="left", padx=12)
        self.txt_log = tk.Text(f, wrap="none", font=("Consolas", 9), state="disabled")
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refrescar_log(self):
        try:
            lineas = RUTA_LOG.read_text(encoding="utf-8").splitlines()[-300:]
            self._set_texto(self.txt_log, "\n".join(lineas))
            self.txt_log.see("end")
        except OSError as e:
            log.error("No se pudo leer el log: %s", e)

    # ---------------- refresco de tablas y listas ----------------
    def refrescar(self):
        # se conserva la fila seleccionada de cada tabla tras actualizar
        previas = {tv: tv.selection() for tv in
                   (self.tv_clientes, self.tv_servicios, self.tv_reservas)}
        for tv in previas:
            tv.delete(*tv.get_children())
        for c in self.clientes:
            self.tv_clientes.insert("", "end", iid=str(c.id),
                                    values=(c.id, c.nombre, c.documento, c.email, c.telefono))
        for s in self.servicios:
            self.tv_servicios.insert("", "end", iid=str(s.id), values=(
                s.id, s.TIPO, s.nombre, f"${s.tarifa_hora:,.0f}", s.detalle(),
                "Sí" if s.disponible else "NO"))
        for r in self.reservas:
            total = f"${r.costo:,.2f}" if r.costo is not None else "-"
            self.tv_reservas.insert("", "end", iid=str(r.id), tags=(r.estado.value,), values=(
                r.id, r.cliente.nombre, r.servicio.nombre, r.horas, r.estado.value, total))
        for tv, sel in previas.items():
            if sel and tv.exists(sel[0]):
                tv.selection_set(sel[0])
        self.r_cli["values"] = [f"{c.id} - {c.nombre}" for c in self.clientes]
        self.r_srv["values"] = [f"{s.id} - {s.nombre} ({s.TIPO})" for s in self.servicios]


def main():
    try:
        app = App()
    except tk.TclError as e:
        log.critical("No se pudo abrir la ventana: %s", e)
        print("No se pudo abrir la interfaz gráfica (¿entorno sin pantalla?):", e)
        return
    app.mainloop()


if __name__ == "__main__":
    main()
