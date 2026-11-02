"""Módulo de gestión de inventario para EcoTech Solutions.

Incluye el modelo de productos (jerarquía de dispositivos), excepciones de
negocio para el stock y persistencia del catálogo en formato JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StockInvalidoError(Exception):
    """Excepción lanzada cuando se viola la regla de negocio del stock.

    El stock de un dispositivo nunca puede ser negativo.
    """


class DispositivoEcologico:
    """Representa un dispositivo ecológico genérico del catálogo.

    Attributes:
        id_producto: Identificador único del producto.
        nombre: Nombre comercial del dispositivo.
        precio: Precio unitario del dispositivo.
        stock: Cantidad disponible en inventario (no negativa).
    """

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio: float,
        stock: int,
    ) -> None:
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        # Se asigna a través del setter para validar la regla de negocio.
        self.stock = stock

    @property
    def stock(self) -> int:
        """Cantidad disponible en inventario (solo lectura externa)."""
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        """Valida y asigna el stock, prohibiendo valores negativos."""
        if valor < 0:
            raise StockInvalidoError(
                f"El stock no puede ser negativo (valor recibido: {valor})."
            )
        self._stock = valor

    def generar_ficha_tecnica(self) -> str:
        """Genera una cadena con los datos básicos del dispositivo."""
        return (
            f"ID: {self.id_producto} | Nombre: {self.nombre} | "
            f"Precio: {self.precio:.2f} | Stock: {self.stock}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convierte el dispositivo a diccionario para serialización JSON."""
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }


class PanelSolar(DispositivoEcologico):
    """Panel solar, especialización de :class:`DispositivoEcologico`.

    Attributes:
        potencia_w: Potencia nominal en vatios.
        eficiencia_porcentaje: Eficiencia de conversión en porcentaje.
    """

    def __init__(
        self,
        id_producto: str,
        nombre: str,
        precio: float,
        stock: int,
        potencia_w: int,
        eficiencia_porcentaje: float,
    ) -> None:
        super().__init__(id_producto, nombre, precio, stock)
        self.potencia_w = potencia_w
        self.eficiencia_porcentaje = eficiencia_porcentaje

    def generar_ficha_tecnica(self) -> str:
        """Ficha técnica polimórfica con datos específicos del panel solar."""
        base = super().generar_ficha_tecnica()
        return (
            f"{base} | Potencia: {self.potencia_w} W | "
            f"Eficiencia: {self.eficiencia_porcentaje:.1f}%"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convierte el panel solar a diccionario para serialización JSON."""
        datos = super().to_dict()
        datos.update(
            {
                "potencia_w": self.potencia_w,
                "eficiencia_porcentaje": self.eficiencia_porcentaje,
            }
        )
        return datos


class GestorInventario:
    """Gestiona la persistencia del catálogo de dispositivos."""

    @staticmethod
    def guardar_catalogo_json(
        lista_dispositivos: list[DispositivoEcologico],
        ruta_archivo: str | Path,
    ) -> None:
        """Serializa una lista de dispositivos a un archivo JSON.

        Args:
            lista_dispositivos: Dispositivos a persistir.
            ruta_archivo: Ruta del archivo de destino.

        Raises:
            OSError: Si ocurre un error de E/S al escribir el archivo.
        """
        datos = [
            dispositivo.to_dict() if hasattr(dispositivo, "to_dict") else {}
            for dispositivo in lista_dispositivos
        ]

        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
            archivo.write("\n")


__all__ = [
    "StockInvalidoError",
    "DispositivoEcologico",
    "PanelSolar",
    "GestorInventario",
]


if __name__ == "__main__":
    # --- Demostración de captura controlada de StockInvalidoError ---
    print("=== Validación de regla de negocio (stock) ===")

    # Intento de instanciación con stock negativo.
    try:
        dispositivo_invalido = DispositivoEcologico(
            "D-INVALIDO", "Dispositivo Inválido", 99.99, -3
        )
    except StockInvalidoError as error:
        print(f"Capturado al instanciar: {error}")

    # Intento de modificación con stock negativo.
    try:
        panel_temporal = PanelSolar(
            "P-TEMP", "Panel Temporal", 200.0, 2, 100, 15.0
        )
        panel_temporal.stock = -1
    except StockInvalidoError as error:
        print(f"Capturado al modificar: {error}")

    # --- Catálogo de productos válidos ---
    print("\n=== Fichas técnicas (polimorfismo) ===")
    catalogo: list[DispositivoEcologico] = [
        DispositivoEcologico("D001", "Sensor de Humedad Eco", 120.50, 15),
        DispositivoEcologico("D002", "Medidor de Calidad de Aire", 89.99, 8),
        PanelSolar("P001", "Panel Solar 300W", 450.00, 5, 300, 21.5),
        PanelSolar("P002", "Panel Solar 450W Bifacial", 620.00, 3, 450, 22.3),
    ]

    for producto in catalogo:
        print(producto.generar_ficha_tecnica())

    # --- Persistencia en disco ---
    ruta_catalogo = "catalogo_ecotech.json"
    GestorInventario.guardar_catalogo_json(catalogo, ruta_catalogo)
    print(f"\nCatálogo exportado exitosamente a '{ruta_catalogo}'.")
