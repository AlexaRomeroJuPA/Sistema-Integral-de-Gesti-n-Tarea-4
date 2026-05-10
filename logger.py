"""
logger.py - Sistema de Logging del Software FJ
Autor: Equipo Software FJ
Descripción: Registra todos los eventos, errores y operaciones del sistema
             en el archivo logs.txt con formato estructurado.
"""

import os
from datetime import datetime
from typing import Optional


class Logger:
    """
    Clase singleton que gestiona el registro de eventos y errores del sistema.
    Encapsula toda la lógica de escritura en el archivo de logs.
    """

    _instancia: Optional["Logger"] = None
    _RUTA_LOGS = os.path.join(os.path.dirname(__file__), "logs.txt")

    # ──────────────────────────────────────────────────────
    # Patrón Singleton
    # ──────────────────────────────────────────────────────
    def __new__(cls) -> "Logger":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        """Inicializa el archivo de logs con encabezado de sesión."""
        try:
            with open(self._RUTA_LOGS, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 70 + "\n")
                f.write(f"  SESIÓN INICIADA: {self._timestamp()}\n")
                f.write(f"  Sistema: Software FJ - Gestión de Clientes, Servicios y Reservas\n")
                f.write("=" * 70 + "\n")
        except OSError as e:
            print(f"[LOGGER] No se pudo inicializar el archivo de logs: {e}")

    # ──────────────────────────────────────────────────────
    # Métodos públicos de registro
    # ──────────────────────────────────────────────────────
    def info(self, mensaje: str, origen: str = "SISTEMA") -> None:
        """Registra un evento informativo."""
        self._escribir("INFO ", origen, mensaje)

    def advertencia(self, mensaje: str, origen: str = "SISTEMA") -> None:
        """Registra una advertencia."""
        self._escribir("WARN ", origen, mensaje)

    def error(self, mensaje: str, origen: str = "SISTEMA",
              excepcion: Optional[Exception] = None) -> None:
        """Registra un error, opcionalmente con detalles de la excepción."""
        detalle = f"{mensaje}"
        if excepcion is not None:
            detalle += f" | Excepción: {type(excepcion).__name__}: {excepcion}"
            # Encadenamiento: causa raíz
            if excepcion.__cause__:
                detalle += f" | Causa: {excepcion.__cause__}"
        self._escribir("ERROR", origen, detalle)

    def operacion(self, operacion: str, resultado: str,
                  origen: str = "SISTEMA") -> None:
        """Registra el resultado de una operación del sistema."""
        self._escribir("OPER ", origen, f"{operacion} → {resultado}")

    # ──────────────────────────────────────────────────────
    # Método privado de escritura
    # ──────────────────────────────────────────────────────
    def _escribir(self, nivel: str, origen: str, mensaje: str) -> None:
        linea = f"[{self._timestamp()}] [{nivel}] [{origen:<12}] {mensaje}\n"
        try:
            with open(self._RUTA_LOGS, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError:
            # Si no se puede escribir en el log, al menos mostrar en consola
            print(f"[LOG-FALLBACK] {linea.strip()}")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
