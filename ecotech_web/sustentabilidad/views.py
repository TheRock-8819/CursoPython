from __future__ import annotations

import os
import sys

# Permite importar Ejercicio3.py desde la raíz del repositorio.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from Ejercicio3 import obtener_metricas_consumo

from django.shortcuts import render


def vista_panel_sustentabilidad(request):
    historial_simulado = [
        {"planta": "Planta A", "consumo_kwh": 1200.0, "factor_emision": 0.4},
        {"planta": "Planta B", "consumo_kwh": 850.0, "factor_emision": 0.35},
        {"planta": "Planta C", "consumo_kwh": 2100.0, "factor_emision": 0.42},
    ]
    contexto = obtener_metricas_consumo(historial_simulado)
    return render(request, "sustentabilidad/panel.html", contexto)
