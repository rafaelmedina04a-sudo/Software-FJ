"""Punto de entrada de Software FJ.

Uso:
    python main.py              abre la interfaz gráfica (Tkinter)
    python main.py --consola    ejecuta la simulación de 18 operaciones en la terminal
"""
import sys

from registro import log


def main():
    if "--consola" in sys.argv[1:]:
        from simulacion import simulacion_demo
        simulacion_demo(print)
        return

    import tkinter as tk
    from interfaz import App
    try:
        app = App()
    except tk.TclError as e:
        log.critical("No se pudo abrir la ventana: %s", e)
        print("No se pudo abrir la interfaz gráfica (¿entorno sin pantalla?):", e)
        print("Use 'python main.py --consola' para ejecutar la simulación en la terminal.")
        return
    app.mainloop()


if __name__ == "__main__":
    main()
