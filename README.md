# Software FJ

Sistema integral de gestión de **clientes, servicios y reservas**, desarrollado en Python con
programación orientada a objetos y manejo avanzado de excepciones. No usa base de datos: todo
se guarda en objetos y listas en memoria, y los archivos se usan solo para el registro de eventos (log).

## Requisitos

- Python 3.9 o superior.
- Tkinter (viene incluido con Python en Windows y macOS; en Linux: `sudo apt install python3-tk`).
- No requiere instalar librerías externas.

## Cómo ejecutarlo

```bash
git clone https://github.com/<usuario>/Software-FJ.git
cd Software-FJ
python main.py              # abre la interfaz gráfica
python main.py --consola    # ejecuta la simulación de 18 operaciones en la terminal
```

### Dos formas de ejecución

| Comando | Qué hace |
|---|---|
| `python main.py` | Abre la **interfaz gráfica** (Tkinter), sin argumentos. |
| `python main.py --consola` | Ejecuta la **simulación de consola** de 18 operaciones (válidas e inválidas) e imprime el resultado en la terminal. |

Las evidencias de ejecución (salida de consola y contenido del log) se toman con
`python main.py --consola`.

## Registro de eventos (logs)

Cada ejecución escribe en `logs/software_fj.log` (la carpeta se crea sola). El archivo registra
altas de clientes y servicios, creación, confirmación y procesamiento de reservas, y todos los
errores controlados con su causa. Ejemplo de líneas:

```
INFO     | Cliente registrado: Ana Pérez (doc 1012345678)
ERROR    | Cliente no creado: Email inválido: 'carlos-sin-arroba'
ERROR    | Demo 18 'Reserva con cliente nulo' falló: La reserva requiere un Cliente válido
```

La carpeta `logs/` está en `.gitignore`: el log se genera al ejecutar y no se sube al repositorio.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `main.py` | Punto de entrada del programa. |
| `excepciones.py` | Excepciones personalizadas (`ErrorSoftwareFJ` y sus derivadas). |
| `registro.py` | Configuración del log en `logs/software_fj.log`. |
| `entidades.py` | Clase abstracta `Entidad` y clase `Cliente` con validaciones. |
| `servicios.py` | Clase abstracta `Servicio` y los servicios `ReservaSala`, `AlquilerEquipo` y `Asesoria`. |
| `reservas.py` | Enum `Estado` y clase `Reserva` (confirmar, cancelar, procesar). |
| `simulacion.py` | Simulación automática de 18 operaciones válidas e inválidas. |
| `interfaz.py` | Interfaz gráfica con Tkinter (clientes, servicios, reservas, simulación y log). |

Dependencias entre módulos: `main` → `interfaz` / `simulacion` → `reservas` → `servicios` →
`entidades` → `excepciones` y `registro`.

## Conceptos de POO aplicados

- **Abstracción:** `Entidad` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`).
- **Herencia y polimorfismo:** los tres servicios especializados implementan su propia validación,
  cálculo de costo y detalle.
- **Encapsulación:** atributos privados con propiedades y validación en los setters.
- **Sobrecarga simulada:** `calcular_costo(horas)`, `calcular_costo(horas, impuesto)`,
  `calcular_costo(horas, impuesto, descuento)` y con parámetros nombrados.

## Manejo de excepciones

- Jerarquía propia que parte de `ErrorSoftwareFJ`.
- Uso de `try / except / else / finally`.
- Encadenamiento de excepciones (`raise ... from e`) para conservar la causa original.
- Ningún error detiene el sistema: se registra en el log y se informa al usuario.

## Servicios disponibles

| Servicio | Horas permitidas | Cálculo |
|---|---|---|
| Reserva de sala | 1 a 12 | tarifa × horas |
| Alquiler de equipo | 1 a 72 | tarifa × horas × cantidad + seguro |
| Asesoría especializada | 0.5 a 8 | tarifa × horas × recargo (junior 1.0, senior 1.5, experto 2.0) |

El IVA por defecto es 19 %.

## Estados de una reserva

`Pendiente` → `Confirmada` → `Procesada`. Una reserva puede cancelarse mientras no esté
procesada o cancelada.

## Integrantes y aportes

| Integrante | Qué desarrolló | Rama | Pull request |
|---|---|---|---|
| Rafael Medina | ( excepciones.py) | (rafael-excepciones) | (9) |
| Josue  Ruiz   | Programa original en un solo archivo y reorganización en módulos | `reorganizar-modulos` | (#) |
| Jesus Durango | (registro) | (rama) | (#) |
| Sandri Martinez | (Entidades) | (rama) | (#) |
| Jesus quintero| (Servicios) | (rama) | (#) |

La reorganización final en módulos (`excepciones.py`, `registro.py`, `entidades.py`, `servicios.py`,
`reservas.py`, `simulacion.py`, `interfaz.py` y `main.py`) se integró desde la rama
`reorganizar-modulos`. Los aportes previos de cada integrante (fragmentos iniciales, ramas y
pull requests #7 y #8) están en el historial de commits del repositorio.

## Flujo de trabajo

Cada integrante trabaja en una rama propia y los cambios se integran a `main` mediante pull requests,
con mensajes de commit que describen lo que se hizo.
