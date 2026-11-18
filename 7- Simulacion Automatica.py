# =====================================================================
# 6. SIMULACIÓN AUTOMÁTICA (18 operaciones, independiente de la pantalla)
# =====================================================================
def simulacion_demo(emit):
    """Ejecuta 18 operaciones válidas e inválidas; 'emit' recibe cada línea de salida."""
    log.info("=== Inicio de simulación automática ===")
    d_cli, d_srv, d_res = [], [], []

    def reg_cliente(*a):
        c = Cliente(*a)
        d_cli.append(c)
        return c

    def reg_servicio(clase, *a):
        s = clase(*a)
        d_srv.append(s)
        return s

    def reservar(i_cli, i_srv, horas, confirmar=True, procesar=True):
        r = Reserva(d_cli[i_cli], d_srv[i_srv], horas)
        d_res.append(r)
        if confirmar:
            r.confirmar()
        if procesar:
            r.procesar()
        return r.describir()

    ops = [
        ("Cliente válido (Ana)", lambda: reg_cliente("ana pérez", "1012345678", "ana@correo.com", "3001234567")),
        ("Cliente válido (Luis)", lambda: reg_cliente("Luis Gómez", "79876543", "luis@mail.co", "3109876543")),
        ("Cliente inválido (email malo)", lambda: reg_cliente("Carlos Ruiz", "123456789", "carlos-sin-arroba", "3201112233")),
        ("Cliente inválido (documento con letras)", lambda: reg_cliente("Marta Díaz", "12AB56", "marta@mail.com", "3201112233")),
        ("Servicio válido: sala", lambda: reg_servicio(ReservaSala, "Sala Innovación", 50000, 12)),
        ("Servicio válido: equipo", lambda: reg_servicio(AlquilerEquipo, "Proyector 4K", 8000, 2, 15000)),
        ("Servicio válido: asesoría", lambda: reg_servicio(Asesoria, "Asesoría Cloud", 70000, "senior")),
        ("Servicio inválido (tarifa negativa)", lambda: reg_servicio(ReservaSala, "Sala X", -100, 5)),
        ("Servicio inválido (nivel desconocido)", lambda: reg_servicio(Asesoria, "Asesoría Y", 60000, "maestro")),
        ("Reserva exitosa (Ana, sala 3h)", lambda: reservar(0, 0, 3)),
        ("Reserva fallida (20h en sala)", lambda: reservar(1, 0, 20)),
        ("Reserva fallida (servicio no disponible)",
         lambda: (d_srv[1].cambiar_disponibilidad(False), reservar(1, 1, 5))[1]),
        ("Reserva exitosa (Luis, asesoría 2h)", lambda: reservar(1, 2, 2)),
        ("Procesar sin confirmar", lambda: reservar(0, 2, 1, confirmar=False)),
        ("Cancelar una reserva ya procesada", lambda: d_res[0].cancelar()),
        ("Cálculo con descuento fuera de rango", lambda: d_srv[0].calcular_costo(2, 0.19, 1.5)),
        ("Sobrecarga de costo (variantes)", lambda: {
            "base": d_srv[0].calcular_costo(2),
            "con IVA": d_srv[0].calcular_costo_con_iva(2),
            "IVA+desc 10%": d_srv[0].calcular_costo(2, 0.19, 0.10),
            "nombrado": d_srv[0].calcular_costo(2, impuesto=0.05)}),
        ("Reserva con cliente nulo", lambda: Reserva(None, d_srv[0], 2)),
    ]
    exitos = errores = 0
    for i, (titulo, accion) in enumerate(ops, 1):
        emit(f"[{i:02d}] {titulo}")
        try:
            res = accion()
        except ErrorSoftwareFJ as e:
            causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
            log.error("Demo %02d '%s' falló: %s%s", i, titulo, e, causa)
            emit(f"      ✖ ERROR controlado: {e}{causa}")
            errores += 1
        except Exception as e:
            log.critical("Demo %02d error inesperado: %r", i, e, exc_info=True)
            emit(f"      ✖ ERROR inesperado controlado: {e!r}")
            errores += 1
        else:
            log.info("Demo %02d '%s' exitosa", i, titulo)
            emit(f"      ✔ {res}")
            exitos += 1
        finally:
            log.info("Demo %02d terminada", i)
    emit("")
    emit(f"=== Fin: {exitos} operaciones exitosas y {errores} errores controlados. "
         f"El sistema siguió estable. ===")
    log.info("=== Fin de simulación automática ===")
