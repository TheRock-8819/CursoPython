from __future__ import annotations

import sys
from pathlib import Path

from django.shortcuts import render

# Ejercicio3.py está en la raíz del repositorio, fuera del paquete Django.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from Ejercicio3 import obtener_metricas_consumo


def vista_panel_sustentabilidad(request):
    historial_simulado = [
        {"planta": "Planta A", "consumo_kwh": 1200.0, "factor_emision": 0.4},
        {"planta": "Planta B", "consumo_kwh": 850.0, "factor_emision": 0.35},
        {"planta": "Planta C", "consumo_kwh": 2100.0, "factor_emision": 0.42},
    ]
    contexto = obtener_metricas_consumo(historial_simulado)
    return render(request, "sustentabilidad/panel.html", contexto)
