"""
Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
VERSIÓN CON PANTALLA INTERACTIVA (interfaz gráfica con Tkinter). Todo en un solo archivo.

POO + manejo avanzado de excepciones. Sin base de datos: todo en objetos y listas;
archivos solo para logs.

Ejecución:  python software_fj_gui.py        (Tkinter viene incluido con Python)
"""
import logging
import re
import tkinter as tk
from abc import ABC, abstractmethod
from enum import Enum
from itertools import count
from pathlib import Path
from tkinter import messagebox, ttk
