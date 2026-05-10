"""
servicio.py - Servicios del Sistema Software FJ
Autor: Equipo Software FJ
Descripción: Define la clase abstracta Servicio y tres implementaciones
             concretas: ReservaSala, AlquilerEquipo y AsesoriaEspecializada.
             Aplica herencia, polimorfismo y métodos sobrescritos.
"""

from abc import abstractmethod
from typing import Optional

from cliente import EntidadSistema
from excepciones import (
    CapacidadExcedidaError,
    ParametroServicioInvalidoError,
    ServicioNoDisponibleError,
)
from logger import Logger


# ══════════════════════════════════════════════════════════════════════════════
# Clase Abstracta Servicio (hereda de EntidadSistema → HERENCIA en cadena)
# ══════════════════════════════════════════════════════════════════════════════
class Servicio(EntidadSistema):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.
    Aplica ABSTRACCIÓN y POLIMORFISMO: cada subclase implementa sus propios
    métodos de cálculo de costo y descripción.
    """

    _logger = Logger()
    _IVA_DEFAULT = 0.19          # 19 % de IVA
    _DESCUENTO_CORP = 0.10       # 10 % para clientes corporativos

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        precio_hora: float,
        disponible: bool = True,
    ) -> None:
        if not servicio_id or len(str(servicio_id)) < 2:
            raise ParametroServicioInvalidoError(
                "servicio_id", servicio_id, "Debe tener al menos 2 caracteres."
            )
        if precio_hora <= 0:
            raise ParametroServicioInvalidoError(
                "precio_hora", precio_hora, "Debe ser un valor positivo."
            )
        self.__servicio_id = str(servicio_id).strip()
        self.__nombre = str(nombre).strip()
        self.__precio_hora = float(precio_hora)
        self.__disponible = bool(disponible)

    # ──────────────────────────────────────────────────────
    # Propiedades base
    # ──────────────────────────────────────────────────────
    @property
    def servicio_id(self) -> str:
        return self.__servicio_id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def precio_hora(self) -> float:
        return self.__precio_hora

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self.__disponible = bool(valor)

    # ──────────────────────────────────────────────────────
    # Implementación de EntidadSistema
    # ──────────────────────────────────────────────────────
    def obtener_id(self) -> str:
        return self.__servicio_id

    def validar(self) -> bool:
        return self.__disponible and self.__precio_hora > 0

    def verificar_disponibilidad(self) -> None:
        """Lanza excepción si el servicio no está disponible."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)

    # ──────────────────────────────────────────────────────
    # Métodos abstractos (Polimorfismo)
    # ──────────────────────────────────────────────────────
    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        """Calcula el costo base del servicio para la duración dada."""
        ...

    @abstractmethod
    def calcular_costo_con_impuesto(
        self, horas: float, iva: float = _IVA_DEFAULT
    ) -> float:
        """Calcula el costo incluyendo IVA (método sobrecargado por parámetros)."""
        ...

    @abstractmethod
    def calcular_costo_con_descuento(
        self,
        horas: float,
        descuento: float = _DESCUENTO_CORP,
        aplicar_iva: bool = False,
    ) -> float:
        """Calcula el costo con descuento opcional e IVA opcional."""
        ...

    @abstractmethod
    def describir(self) -> str:
        ...

    # ──────────────────────────────────────────────────────
    # Gestión de servicios (lista interna)
    # ──────────────────────────────────────────────────────
    _servicios: dict = {}  # {servicio_id: Servicio}

    @classmethod
    def registrar(cls, servicio: "Servicio") -> None:
        from excepciones import ServicioError
        cls._servicios[servicio.servicio_id] = servicio
        cls._logger.operacion(
            f"Registro de servicio '{servicio.servicio_id}'", "EXITOSO", "SERVICIO"
        )

    @classmethod
    def buscar(cls, servicio_id: str) -> "Servicio":
        from excepciones import ServicioNoEncontradoError
        if servicio_id not in cls._servicios:
            raise ServicioNoEncontradoError(servicio_id)
        return cls._servicios[servicio_id]

    @classmethod
    def listar(cls) -> list:
        return list(cls._servicios.values())


# ══════════════════════════════════════════════════════════════════════════════
# Servicio 1: ReservaSala
# ══════════════════════════════════════════════════════════════════════════════
class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión o conferencia.
    POLIMORFISMO: sobrescribe calcular_costo para incluir cargo por capacidad.
    """

    PRECIO_POR_PERSONA_HORA = 5_000  # COP adicional por persona

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        precio_hora: float,
        capacidad_max: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(servicio_id, nombre, precio_hora, disponible)
        if capacidad_max < 1:
            raise ParametroServicioInvalidoError(
                "capacidad_max", capacidad_max, "Debe ser al menos 1."
            )
        self.__capacidad_max = int(capacidad_max)

    @property
    def capacidad_max(self) -> int:
        return self.__capacidad_max

    # ── Polimorfismo: métodos sobrescritos ──────────────────
    def calcular_costo(self, horas: float, personas: int = 1) -> float:
        """
        Costo = precio_hora * horas + cargo_por_persona.
        SOBRECARGA SIMULADA: acepta parámetro opcional 'personas'.
        """
        self.verificar_disponibilidad()
        if horas <= 0:
            raise ParametroServicioInvalidoError("horas", horas, "Debe ser mayor a 0.")
        if personas > self.__capacidad_max:
            raise CapacidadExcedidaError(self.nombre, self.__capacidad_max)
        cargo_extra = self.PRECIO_POR_PERSONA_HORA * personas * horas
        return self.precio_hora * horas + cargo_extra

    def calcular_costo_con_impuesto(
        self, horas: float, iva: float = Servicio._IVA_DEFAULT, personas: int = 1
    ) -> float:
        """Costo con IVA incluido."""
        base = self.calcular_costo(horas, personas)
        return base * (1 + iva)

    def calcular_costo_con_descuento(
        self,
        horas: float,
        descuento: float = Servicio._DESCUENTO_CORP,
        aplicar_iva: bool = False,
        personas: int = 1,
    ) -> float:
        """Costo con descuento corporativo e IVA opcional."""
        base = self.calcular_costo(horas, personas)
        total = base * (1 - descuento)
        return total * (1 + self._IVA_DEFAULT) if aplicar_iva else total

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[ReservaSala] ID: {self.servicio_id} | {self.nombre} | "
            f"${self.precio_hora:,.0f}/h | Cap. máx: {self.__capacidad_max} personas | "
            f"Estado: {estado}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Servicio 2: AlquilerEquipo
# ══════════════════════════════════════════════════════════════════════════════
class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    POLIMORFISMO: sobrescribe calcular_costo para incluir seguro por equipo.
    """

    SEGURO_PORCENTAJE = 0.05  # 5 % del costo base por seguro obligatorio

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        precio_hora: float,
        tipo_equipo: str,
        requiere_deposito: bool = True,
        deposito: float = 0.0,
        disponible: bool = True,
    ) -> None:
        super().__init__(servicio_id, nombre, precio_hora, disponible)
        if not tipo_equipo.strip():
            raise ParametroServicioInvalidoError(
                "tipo_equipo", tipo_equipo, "No puede estar vacío."
            )
        if deposito < 0:
            raise ParametroServicioInvalidoError(
                "deposito", deposito, "No puede ser negativo."
            )
        self.__tipo_equipo = tipo_equipo.strip()
        self.__requiere_deposito = requiere_deposito
        self.__deposito = float(deposito)

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def deposito(self) -> float:
        return self.__deposito

    # ── Polimorfismo ──────────────────────────────────────
    def calcular_costo(self, horas: float, incluir_seguro: bool = True) -> float:
        """
        Costo = precio_hora * horas [+ seguro].
        SOBRECARGA SIMULADA: parámetro 'incluir_seguro'.
        """
        self.verificar_disponibilidad()
        if horas <= 0:
            raise ParametroServicioInvalidoError("horas", horas, "Debe ser mayor a 0.")
        base = self.precio_hora * horas
        seguro = base * self.SEGURO_PORCENTAJE if incluir_seguro else 0
        return base + seguro + (self.__deposito if self.__requiere_deposito else 0)

    def calcular_costo_con_impuesto(
        self, horas: float, iva: float = Servicio._IVA_DEFAULT,
        incluir_seguro: bool = True
    ) -> float:
        base = self.calcular_costo(horas, incluir_seguro)
        return base * (1 + iva)

    def calcular_costo_con_descuento(
        self,
        horas: float,
        descuento: float = Servicio._DESCUENTO_CORP,
        aplicar_iva: bool = False,
        incluir_seguro: bool = True,
    ) -> float:
        base = self.calcular_costo(horas, incluir_seguro)
        total = base * (1 - descuento)
        return total * (1 + self._IVA_DEFAULT) if aplicar_iva else total

    def describir(self) -> str:
        deposito_txt = f"Depósito: ${self.__deposito:,.0f}" if self.__requiere_deposito else "Sin depósito"
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[AlquilerEquipo] ID: {self.servicio_id} | {self.nombre} | "
            f"Tipo: {self.__tipo_equipo} | ${self.precio_hora:,.0f}/h | "
            f"{deposito_txt} | Estado: {estado}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Servicio 3: AsesoriaEspecializada
# ══════════════════════════════════════════════════════════════════════════════
class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría especializada por consultores certificados.
    POLIMORFISMO: tarifa variable según nivel del asesor.
    """

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(
        self,
        servicio_id: str,
        nombre: str,
        precio_hora: float,
        area: str,
        nivel_asesor: str = "senior",
        disponible: bool = True,
    ) -> None:
        super().__init__(servicio_id, nombre, precio_hora, disponible)
        if not area.strip():
            raise ParametroServicioInvalidoError(
                "area", area, "El área de asesoría no puede estar vacía."
            )
        nivel = nivel_asesor.lower().strip()
        if nivel not in self.NIVELES:
            raise ParametroServicioInvalidoError(
                "nivel_asesor", nivel_asesor,
                f"Niveles válidos: {list(self.NIVELES.keys())}"
            )
        self.__area = area.strip()
        self.__nivel_asesor = nivel

    @property
    def area(self) -> str:
        return self.__area

    @property
    def nivel_asesor(self) -> str:
        return self.__nivel_asesor

    def _multiplicador(self) -> float:
        return self.NIVELES[self.__nivel_asesor]

    # ── Polimorfismo ──────────────────────────────────────
    def calcular_costo(self, horas: float, sesiones: int = 1) -> float:
        """
        Costo = precio_hora * multiplicador_nivel * horas * sesiones.
        SOBRECARGA SIMULADA: parámetro opcional 'sesiones'.
        """
        self.verificar_disponibilidad()
        if horas <= 0:
            raise ParametroServicioInvalidoError("horas", horas, "Debe ser mayor a 0.")
        if sesiones < 1:
            raise ParametroServicioInvalidoError("sesiones", sesiones, "Mínimo 1 sesión.")
        return self.precio_hora * self._multiplicador() * horas * sesiones

    def calcular_costo_con_impuesto(
        self, horas: float, iva: float = Servicio._IVA_DEFAULT, sesiones: int = 1
    ) -> float:
        return self.calcular_costo(horas, sesiones) * (1 + iva)

    def calcular_costo_con_descuento(
        self,
        horas: float,
        descuento: float = Servicio._DESCUENTO_CORP,
        aplicar_iva: bool = False,
        sesiones: int = 1,
    ) -> float:
        base = self.calcular_costo(horas, sesiones)
        total = base * (1 - descuento)
        return total * (1 + self._IVA_DEFAULT) if aplicar_iva else total

    def describir(self) -> str:
        mult = self._multiplicador()
        tarifa_real = self.precio_hora * mult
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[AsesoriaEspecializada] ID: {self.servicio_id} | {self.nombre} | "
            f"Área: {self.__area} | Nivel: {self.__nivel_asesor.capitalize()} | "
            f"Tarifa: ${tarifa_real:,.0f}/h | Estado: {estado}"
        )
