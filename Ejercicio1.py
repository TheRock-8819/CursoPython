"""Módulo de sanitización y análisis estadístico de datos de sensores.

Contiene utilidades para normalizar registros crudos de sensores y generar
resúmenes estadísticos (alertas y promedio térmico).
"""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any

UBICACION_POR_DEFECTO: str = "Sin asignar"
def _normalizar_temperatura(valor: Any) -> float:
    """Convierte un valor crudo de temperatura a ``float``.

    Acepta números o cadenas con sufijos de unidad (``C``, ``°C``, espacios).
    También tolera el separador decimal con coma.
    """
    if valor is None:
        raise TypeError("La temperatura no puede ser None.")

    # bool es subclase de int: se excluye para no aceptar True/False como número.
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)

    texto = str(valor).strip()
    if not texto:
        raise ValueError(f"La temperatura está vacía: {valor!r}")

    coincidencia = re.fullmatch(
        r"\s*([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))\s*(?:(?:°|º)?\s*C|C\s*(?:°|º)|grados?)?\s*",
        str(valor),
        flags=re.IGNORECASE,
    )
    if not coincidencia:
        raise ValueError(f"No se pudo convertir la temperatura {valor!r} a float.")
    return float(coincidencia.group(1).replace(",", "."))


def limpiar_registro_sensor(registro_raw: Mapping[str, Any]) -> dict[str, Any]:
    """Sanitiza y estandariza un diccionario de datos crudos de un sensor."""
    if not isinstance(registro_raw, Mapping):
        raise TypeError("registro_raw debe ser un diccionario o mapeo.")

    sensor_id_limpio = str(registro_raw.get("sensor_id", "")).strip()

    if "temperatura" not in registro_raw:
        raise ValueError("El registro no contiene una temperatura.")
    temperatura_raw = registro_raw["temperatura"]
    temperatura_float = _normalizar_temperatura(temperatura_raw)

    # None o texto vacío tras strip se consideran "sin ubicación".
    ubicacion_raw = registro_raw.get("ubicacion")
    if ubicacion_raw is None or str(ubicacion_raw).strip() == "":
        ubicacion_limpia = UBICACION_POR_DEFECTO
    else:
        ubicacion_limpia = str(ubicacion_raw).strip()

    return {
        "sensor_id": sensor_id_limpio,
        "temperatura": temperatura_float,
        "ubicacion": ubicacion_limpia,
    }


def generar_resumen_sensores(
    lista_sensores_limpios: list[dict[str, Any]],
    umbral_temperatura: float,
) -> tuple[list[str], float]:
    """Filtra sensores en alerta y calcula el promedio térmico global."""
    if lista_sensores_limpios is None:
        raise TypeError("lista_sensores_limpios no puede ser None.")

    # Conversión defensiva: un umbral no numérico no debe propagar TypeError opaco.
    try:
        umbral = float(umbral_temperatura)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Umbral de temperatura inválido: {umbral_temperatura!r}") from exc

    # Caso vacío: se evita la división por cero.
    if not lista_sensores_limpios:
        return ([], 0.0)

    sensores_alerta: list[str] = []
    suma_temperaturas: float = 0.0

    for sensor in lista_sensores_limpios:
        temperatura = float(sensor["temperatura"])
        suma_temperaturas += temperatura
        if temperatura > umbral:
            sensores_alerta.append(str(sensor["sensor_id"]))

    promedio_temperatura = suma_temperaturas / len(lista_sensores_limpios)
    return (sensores_alerta, promedio_temperatura)


__all__ = [
    "UBICACION_POR_DEFECTO",
    "limpiar_registro_sensor",
    "generar_resumen_sensores",
]


if __name__ == "__main__":
    registros_crudos: list[dict[str, Any]] = [
        {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
        {"sensor_id": "SENSOR-002", "temperatura": " 31.2 °C ", "ubicacion": ""},
        {"sensor_id": "  SENSOR-003  ", "temperatura": 18.0},
        {"sensor_id": "SENSOR-004", "temperatura": "29.0C", "ubicacion": "   "},
        {"sensor_id": "SENSOR-005", "temperatura": "22,3c", "ubicacion": "Planta Sur"},
    ]

    sensores_limpios = []
    for registro in registros_crudos:
        try:
            sensores_limpios.append(limpiar_registro_sensor(registro))
        except (TypeError, ValueError) as error:
            print(f"Registro inválido omitido: {error}")
    umbral_alerta: float = 25.0
    alertas, promedio = generar_resumen_sensores(sensores_limpios, umbral_alerta)

    print("=" * 62)
    print("REPORTE CONSOLIDADO DE SENSORES")
    print("=" * 62)
    for sensor in sensores_limpios:
        print(
            f"ID: {sensor['sensor_id']:<12} | "
            f"Temp: {sensor['temperatura']:>6.2f} °C | "
            f"Ubicación: {sensor['ubicacion']}"
        )
    print("-" * 62)
    print(f"Umbral de alerta:        {umbral_alerta:>6.2f} °C")
    print(f"Sensores en alerta:      {', '.join(alertas) if alertas else 'Ninguno'}")
    print(f"Promedio térmico global: {promedio:>6.2f} °C")
    print("=" * 62)
