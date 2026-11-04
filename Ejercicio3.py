"""Módulo de auditoría de emisiones y integración web (EcoTech Solutions).

Incluye el algoritmo de cálculo de emisiones de carbono, procesamiento de
métricas de consumo industrial y una vista de Django para el panel de
sustentabilidad.
"""

from __future__ import annotations

import unittest
from typing import Any

# Fallback para entornos sin Django: permite importar/ejecutar el módulo localmente.
try:
    from django.shortcuts import render as django_render
except Exception:  # pragma: no cover - entorno sin Django
    def django_render(request: Any, template_name: str, context: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return {"template": template_name, "context": context or {}}


def calcular_emisiones_carbono(consumo_kwh: float, factor_emision: float = 0.4) -> float:
    """Calcula las emisiones de carbono a partir del consumo energético."""
    if consumo_kwh < 0:
        raise ValueError("El consumo en kWh no puede ser negativo.")
    return consumo_kwh * factor_emision


class TestCalculoEmisiones(unittest.TestCase):
    """Suite de pruebas unitarias para :func:`calcular_emisiones_carbono`."""

    def test_valores_nominales_factor_por_defecto(self) -> None:
        self.assertEqual(calcular_emisiones_carbono(100.0), 40.0)

    def test_valores_nominales_factor_personalizado(self) -> None:
        self.assertEqual(calcular_emisiones_carbono(50.0, 0.35), 17.5)

    def test_consumo_cero(self) -> None:
        self.assertEqual(calcular_emisiones_carbono(0.0), 0.0)
        self.assertEqual(calcular_emisiones_carbono(0.0, 0.9), 0.0)

    def test_consumo_negativo_lanza_value_error(self) -> None:
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-10.0)


def obtener_metricas_consumo(registros: list[dict[str, Any]]) -> dict[str, Any]:
    """Procesa un historial de plantas industriales y calcula métricas."""
    emisiones_por_planta: list[dict[str, Any]] = []
    total_emisiones: float = 0.0
    planta_mayor: dict[str, Any] | None = None

    for registro in registros:
        # Se aceptan variantes de clave para no acoplar el procesador a un esquema único.
        planta = registro.get("planta", registro.get("nombre", registro.get("id", "Sin nombre")))
        consumo = float(registro.get("consumo_kwh", registro.get("consumo", 0.0)))
        factor = float(registro.get("factor_emision", registro.get("factor", 0.4)))

        emision = calcular_emisiones_carbono(consumo, factor)

        detalle = {
            "planta": planta,
            "consumo_kwh": consumo,
            "factor_emision": factor,
            "emisiones": emision,
        }
        emisiones_por_planta.append(detalle)
        total_emisiones += emision

        # Primer registro o consumo estrictamente mayor: actualiza la planta líder.
        if planta_mayor is None or consumo > float(planta_mayor.get("consumo_kwh", 0.0)):
            planta_mayor = detalle

    return {
        "emisiones_por_planta": emisiones_por_planta,
        "total_emisiones": total_emisiones,
        "planta_mayor_consumo": planta_mayor["planta"] if planta_mayor else None,
    }


def vista_panel_sustentabilidad(request: Any) -> Any:
    """Vista de Django que renderiza el panel de sustentabilidad."""
    historial_simulado: list[dict[str, Any]] = [
        {"planta": "Planta A", "consumo_kwh": 1200.0, "factor_emision": 0.4},
        {"planta": "Planta B", "consumo_kwh": 850.0, "factor_emision": 0.35},
        {"planta": "Planta C", "consumo_kwh": 2100.0, "factor_emision": 0.42},
    ]

    contexto = obtener_metricas_consumo(historial_simulado)
    return django_render(request, "sustentabilidad/panel.html", contexto)


__all__ = [
    "calcular_emisiones_carbono",
    "TestCalculoEmisiones",
    "obtener_metricas_consumo",
    "vista_panel_sustentabilidad",
]


if __name__ == "__main__":
    unittest.main(verbosity=2)
