"""Módulo de sanitización y análisis estadístico de datos de sensores.

Contiene utilidades para normalizar registros crudos de sensores y generar
resúmenes estadísticos (alertas y promedio térmico).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# Constantes de configuración
UBICACION_POR_DEFECTO: str = "Sin asignar"
TEMPERATURA_POR_DEFECTO: float = 0.0


def _normalizar_temperatura(valor: Any) -> float:
    """Convierte un valor crudo de temperatura a ``float``.

    Acepta números o cadenas con sufijos de unidad (``C``, ``°C``, espacios).
    También tolera el separador decimal con coma.

    Raises:
        ValueError: Si el valor no puede interpretarse como número.
        TypeError: Si el valor es ``None``.
    """
    if valor is None:
        raise TypeError("La temperatura no puede ser None.")

    # Si ya es numérico, se convierte directamente (evitando bool).
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)

    texto = str(valor).strip()
    if not texto:
        raise ValueError(f"La temperatura está vacía: {valor!r}")

    # Eliminación robusta de sufijos de unidad y espacios.
    texto = texto.replace("°C", "").replace("°c", "").replace("° C", "")
    texto = texto.replace("C", "").replace("c", "").strip()

    # Soporte para coma decimal (formato regional).
    texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError as exc:
        raise ValueError(f"No se pudo convertir la temperatura {valor!r} a float.") from exc


def limpiar_registro_sensor(registro_raw: Mapping[str, Any]) -> dict[str, Any]:
    """Sanitiza y estandariza un diccionario de datos crudos de un sensor.

    Args:
        registro_raw: Diccionario con las claves ``sensor_id``, ``temperatura``
            y opcionalmente ``ubicacion``.

    Returns:
        Nuevo diccionario con los campos normalizados:
        - ``sensor_id`` (str): sin espacios sobrantes.
        - ``temperatura`` (float): valor numérico sin unidades.
        - ``ubicacion`` (str): valor saneado o ``"Sin asignar"``.

    Raises:
        TypeError: Si ``registro_raw`` no es un mapeo.
    """
    if not isinstance(registro_raw, Mapping):
        raise TypeError("registro_raw debe ser un diccionario o mapeo.")

    # 1. Normalizar identificador (remover espacios sobrantes).
    sensor_id_limpio = str(registro_raw.get("sensor_id", "")).strip()

    # 2. Normalizar temperatura a float.
    temperatura_raw = registro_raw.get("temperatura", TEMPERATURA_POR_DEFECTO)
    temperatura_float = _normalizar_temperatura(temperatura_raw)

    # 3. Valor por defecto seguro para ubicación si falta o está vacía.
    ubicacion_raw = registro_raw.get("ubicacion")
    if ubicacion_raw is None or str(ubicacion_raw).strip() == "":
        ubicacion_limpia = UBICACION_POR_DEFECTO
    else:
        ubicacion_limpia = str(ubicacion_raw).strip()

    # Se retorna un NUEVO diccionario (no se muta la entrada).
    return {
        "sensor_id": sensor_id_limpio,
        "temperatura": temperatura_float,
        "ubicacion": ubicacion_limpia,
    }


def generar_resumen_sensores(
    lista_sensores_limpios: list[dict[str, Any]],
    umbral_temperatura: float,
) -> tuple[list[str], float]:
    """Filtra sensores en alerta y calcula el promedio térmico global.

    Args:
        lista_sensores_limpios: Lista de diccionarios sanitizados.
        umbral_temperatura: Temperatura límite (exclusiva) para alerta.

    Returns:
        Tupla ``(lista_sensores_alerta, promedio_temperatura)`` donde
        ``lista_sensores_alerta`` contiene los IDs cuya temperatura supera
        el umbral y ``promedio_temperatura`` es el promedio global.

    Raises:
        TypeError: Si ``lista_sensores_limpios`` no es una lista/iterable.
        ValueError: Si ``umbral_temperatura`` no es convertible a float.
    """
    if lista_sensores_limpios is None:
        raise TypeError("lista_sensores_limpios no puede ser None.")

    try:
        umbral = float(umbral_temperatura)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Umbral de temperatura inválido: {umbral_temperatura!r}") from exc

    # Lista vacía: no hay alertas ni promedio definido (se retorna 0.0).
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
    "TEMPERATURA_POR_DEFECTO",
    "limpiar_registro_sensor",
    "generar_resumen_sensores",
]


if __name__ == "__main__":
    # Colección de prueba con distintas anomalías: espacios sobrantes,
    # temperaturas con unidades, ubicaciones faltantes o vacías.
    registros_crudos: list[dict[str, Any]] = [
        {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
        {"sensor_id": "SENSOR-002", "temperatura": " 31.2 °C ", "ubicacion": ""},
        {"sensor_id": "  SENSOR-003  ", "temperatura": 18.0},  # sin ubicación
        {"sensor_id": "SENSOR-004", "temperatura": "29.0C", "ubicacion": "   "},
        {"sensor_id": "SENSOR-005", "temperatura": "22,3c", "ubicacion": "Planta Sur"},
    ]

    # Sanitización de todos los registros.
    sensores_limpios = [limpiar_registro_sensor(registro) for registro in registros_crudos]

    # Umbral térmico de alerta.
    umbral_alerta: float = 25.0

    # Generación del resumen estadístico.
    alertas, promedio = generar_resumen_sensores(sensores_limpios, umbral_alerta)

    # Reporte consolidado y legible por consola.
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
