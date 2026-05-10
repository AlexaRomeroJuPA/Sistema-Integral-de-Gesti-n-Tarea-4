"""
reserva.py - Clase Reserva del Sistema Software FJ
Autor: Equipo Software FJ
Descripción: Gestiona el ciclo de vida completo de una reserva (PENDIENTE →
             CONFIRMADA → PROCESADA | CANCELADA) con manejo avanzado de
             excepciones: try/except, try/except/else, try/except/finally.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from cliente import Cliente
from excepciones import (
    CostoInsuficienteError,
    DuracionInvalidaError,
    ReservaCanceladaError,
    ReservaNoEncontradaError,
    ReservaYaConfirmadaError,
)
from logger import Logger
from servicio import Servicio


# ══════════════════════════════════════════════════════════════════════════════
# Estado de la Reserva
# ══════════════════════════════════════════════════════════════════════════════
class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


# ══════════════════════════════════════════════════════════════════════════════
# Clase Reserva
# ══════════════════════════════════════════════════════════════════════════════
class Reserva:
    """
    Representa una reserva que integra Cliente, Servicio, duración y estado.
    Implementa el ciclo de vida completo con manejo avanzado de excepciones.
    """

    _logger = Logger()
    _reservas: dict[str, "Reserva"] = {}   # {reserva_id: Reserva}
    DURACION_MINIMA = 0.5                   # horas

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        notas: Optional[str] = None,
        aplicar_descuento: bool = False,
        aplicar_iva: bool = True,
    ) -> None:
        """
        Crea una reserva en estado PENDIENTE.

        Args:
            cliente: Instancia de Cliente ya registrado.
            servicio: Instancia de Servicio disponible.
            duracion_horas: Duración de la reserva en horas (mínimo 0.5).
            notas: Observaciones adicionales (opcional).
            aplicar_descuento: Si True, aplica descuento corporativo del 10 %.
            aplicar_iva: Si True, incluye el 19 % de IVA en el costo.

        Raises:
            DuracionInvalidaError: Si la duración es menor al mínimo.
            ServicioNoDisponibleError: Si el servicio no está disponible.
        """
        # Validar duración
        if duracion_horas < self.DURACION_MINIMA:
            raise DuracionInvalidaError(duracion_horas, self.DURACION_MINIMA)

        # Verificar disponibilidad del servicio
        servicio.verificar_disponibilidad()

        self.__reserva_id = str(uuid.uuid4())[:8].upper()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion_horas = float(duracion_horas)
        self.__notas = notas
        self.__estado = EstadoReserva.PENDIENTE
        self.__fecha_creacion = datetime.now()
        self.__fecha_confirmacion: Optional[datetime] = None
        self.__fecha_cancelacion: Optional[datetime] = None
        self.__aplicar_descuento = aplicar_descuento
        self.__aplicar_iva = aplicar_iva
        self.__costo: Optional[float] = None

        self._logger.info(
            f"Reserva {self.__reserva_id} creada para cliente "
            f"'{cliente.obtener_id()}' | Servicio: '{servicio.nombre}' | "
            f"{duracion_horas}h",
            "RESERVA"
        )

    # ──────────────────────────────────────────────────────
    # Propiedades
    # ──────────────────────────────────────────────────────
    @property
    def reserva_id(self) -> str:
        return self.__reserva_id

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion_horas(self) -> float:
        return self.__duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo(self) -> Optional[float]:
        return self.__costo

    # ──────────────────────────────────────────────────────
    # Ciclo de vida
    # ──────────────────────────────────────────────────────
    def confirmar(self) -> float:
        """
        Confirma la reserva y calcula el costo total.
        Usa try/except/else para separar flujo exitoso del manejo de errores.

        Returns:
            Costo total calculado.

        Raises:
            ReservaYaConfirmadaError: Si ya fue confirmada.
            ReservaCanceladaError: Si está cancelada.
            CostoInsuficienteError: Si el costo calculado es inconsistente.
        """
        if self.__estado == EstadoReserva.CANCELADA:
            raise ReservaCanceladaError(self.__reserva_id)
        if self.__estado == EstadoReserva.CONFIRMADA:
            raise ReservaYaConfirmadaError(self.__reserva_id)

        try:
            # Calcular costo según configuración
            if self.__aplicar_descuento:
                costo = self.__servicio.calcular_costo_con_descuento(
                    self.__duracion_horas,
                    aplicar_iva=self.__aplicar_iva,
                )
            elif self.__aplicar_iva:
                costo = self.__servicio.calcular_costo_con_impuesto(
                    self.__duracion_horas
                )
            else:
                costo = self.__servicio.calcular_costo(self.__duracion_horas)

            # Validar consistencia del costo
            if costo <= 0:
                raise CostoInsuficienteError(costo)

        except (CostoInsuficienteError, Exception) as e:
            self._logger.error(
                f"Error al confirmar reserva {self.__reserva_id}",
                "RESERVA",
                e
            )
            raise  # Re-lanza la excepción para que el caller la maneje
        else:
            # Bloque else: se ejecuta solo si no hubo excepciones
            self.__costo = costo
            self.__estado = EstadoReserva.CONFIRMADA
            self.__fecha_confirmacion = datetime.now()
            self._logger.operacion(
                f"Confirmación reserva {self.__reserva_id}",
                f"EXITOSA | Costo: ${costo:,.0f}",
                "RESERVA"
            )
            return costo

    def procesar(self) -> None:
        """
        Marca la reserva como PROCESADA (servicio entregado).
        Usa try/except/finally para garantizar el registro del intento.

        Raises:
            ReservaError: Si la reserva no está confirmada.
        """
        from excepciones import ReservaError
        try:
            if self.__estado != EstadoReserva.CONFIRMADA:
                raise ReservaError(
                    f"La reserva '{self.__reserva_id}' debe estar CONFIRMADA "
                    f"para procesarse. Estado actual: {self.__estado.value}",
                    "RES-007"
                )
            self.__estado = EstadoReserva.PROCESADA
            self._logger.operacion(
                f"Procesamiento reserva {self.__reserva_id}", "EXITOSO", "RESERVA"
            )
        except Exception as e:
            self._logger.error(
                f"Error al procesar reserva {self.__reserva_id}",
                "RESERVA",
                e
            )
            raise
        finally:
            # Siempre se registra el intento, independientemente del resultado
            self._logger.info(
                f"Intento de procesamiento para reserva {self.__reserva_id} "
                f"(estado final: {self.__estado.value})",
                "RESERVA"
            )

    def cancelar(self, motivo: str = "Sin especificar") -> None:
        """
        Cancela la reserva si no ha sido procesada.

        Args:
            motivo: Razón de la cancelación.

        Raises:
            ReservaError: Si la reserva ya fue procesada.
        """
        from excepciones import ReservaError
        if self.__estado == EstadoReserva.PROCESADA:
            raise ReservaError(
                f"No se puede cancelar la reserva '{self.__reserva_id}': "
                "ya fue procesada.",
                "RES-008"
            )
        self.__estado = EstadoReserva.CANCELADA
        self.__fecha_cancelacion = datetime.now()
        self._logger.operacion(
            f"Cancelación reserva {self.__reserva_id}",
            f"EXITOSA | Motivo: {motivo}",
            "RESERVA"
        )

    # ──────────────────────────────────────────────────────
    # Descripción
    # ──────────────────────────────────────────────────────
    def describir(self) -> str:
        costo_txt = f"${self.__costo:,.0f}" if self.__costo else "Pendiente de cálculo"
        return (
            f"[Reserva {self.__reserva_id}]\n"
            f"  Cliente : {self.__cliente.nombre} ({self.__cliente.cliente_id})\n"
            f"  Servicio: {self.__servicio.nombre}\n"
            f"  Duración: {self.__duracion_horas}h\n"
            f"  Estado  : {self.__estado.value}\n"
            f"  Costo   : {costo_txt}\n"
            f"  Creada  : {self.__fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
        )

    def __repr__(self) -> str:
        return self.describir()

    # ──────────────────────────────────────────────────────
    # Gestión de reservas (lista interna de clase)
    # ──────────────────────────────────────────────────────
    @classmethod
    def agregar(cls, reserva: "Reserva") -> None:
        cls._reservas[reserva.reserva_id] = reserva

    @classmethod
    def buscar(cls, reserva_id: str) -> "Reserva":
        if reserva_id not in cls._reservas:
            raise ReservaNoEncontradaError(reserva_id)
        return cls._reservas[reserva_id]

    @classmethod
    def listar(cls) -> list:
        return list(cls._reservas.values())

    @classmethod
    def listar_por_cliente(cls, cliente_id: str) -> list:
        return [r for r in cls._reservas.values()
                if r.__cliente.cliente_id == cliente_id]
