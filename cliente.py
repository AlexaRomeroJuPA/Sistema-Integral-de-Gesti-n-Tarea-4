"""
cliente.py - Clase Cliente del Sistema Software FJ
Autor: Equipo Software FJ
Descripción: Define la clase Cliente con encapsulación total de datos
             personales, validaciones robustas y manejo de excepciones.
"""

import re
from abc import ABC, abstractmethod
from typing import Optional

from excepciones import DatosClienteInvalidosError
from logger import Logger


# ══════════════════════════════════════════════════════════════════════════════
# Clase Abstracta Base – Entidad del Sistema
# ══════════════════════════════════════════════════════════════════════════════
class EntidadSistema(ABC):
    """
    Clase abstracta que representa cualquier entidad gestionada por el sistema.
    Aplica ABSTRACCIÓN: define el contrato que todas las entidades deben cumplir.
    """

    @abstractmethod
    def obtener_id(self) -> str:
        """Retorna el identificador único de la entidad."""
        ...

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción legible de la entidad."""
        ...

    @abstractmethod
    def validar(self) -> bool:
        """Valida que la entidad esté en un estado consistente."""
        ...

    def __repr__(self) -> str:
        return self.describir()


# ══════════════════════════════════════════════════════════════════════════════
# Clase Cliente
# ══════════════════════════════════════════════════════════════════════════════
class Cliente(EntidadSistema):
    """
    Representa un cliente de Software FJ.

    Aplica ENCAPSULACIÓN: todos los atributos son privados y se acceden
    únicamente a través de propiedades con validación.
    Hereda de EntidadSistema (HERENCIA).
    """

    _logger = Logger()

    # Expresiones regulares de validación
    _RE_EMAIL = re.compile(r"^[\w.\-+]+@[\w\-]+\.[a-zA-Z]{2,}$")
    _RE_TELEFONO = re.compile(r"^\+?[\d\s\-]{7,15}$")
    _RE_ID = re.compile(r"^[A-Za-z0-9\-]{3,20}$")

    def __init__(
        self,
        cliente_id: str,
        nombre: str,
        email: str,
        telefono: str,
        empresa: Optional[str] = None,
    ) -> None:
        """
        Inicializa un cliente con validaciones completas.

        Args:
            cliente_id: Identificador único alfanumérico.
            nombre: Nombre completo (mínimo 3 caracteres).
            email: Correo electrónico válido.
            telefono: Teléfono (7-15 dígitos, puede incluir +, espacios y guiones).
            empresa: Empresa u organización (opcional).

        Raises:
            DatosClienteInvalidosError: Si algún dato no cumple las validaciones.
        """
        # Se usan los setters para disparar validaciones
        self.cliente_id = cliente_id    # llama al setter
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.__empresa: Optional[str] = empresa.strip() if empresa else None

        self._logger.info(
            f"Cliente creado: {self.__nombre} ({self.__cliente_id})",
            "CLIENTE"
        )

    # ──────────────────────────────────────────────────────
    # Propiedades (Encapsulación)
    # ──────────────────────────────────────────────────────
    @property
    def cliente_id(self) -> str:
        return self.__cliente_id

    @cliente_id.setter
    def cliente_id(self, valor: str) -> None:
        valor = str(valor).strip()
        if not self._RE_ID.match(valor):
            raise DatosClienteInvalidosError(
                "cliente_id", valor,
                "Debe tener entre 3 y 20 caracteres alfanuméricos o guiones."
            )
        self.__cliente_id = valor

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if len(valor) < 3:
            raise DatosClienteInvalidosError(
                "nombre", valor, "Debe tener al menos 3 caracteres."
            )
        if not all(c.isalpha() or c in " .-'" for c in valor):
            raise DatosClienteInvalidosError(
                "nombre", valor,
                "Solo se permiten letras, espacios, puntos, guiones y apostrofes."
            )
        self.__nombre = valor

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str) -> None:
        valor = str(valor).strip().lower()
        if not self._RE_EMAIL.match(valor):
            raise DatosClienteInvalidosError(
                "email", valor, "Formato de correo electrónico inválido."
            )
        self.__email = valor

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        valor = str(valor).strip()
        if not self._RE_TELEFONO.match(valor):
            raise DatosClienteInvalidosError(
                "telefono", valor,
                "Debe contener entre 7 y 15 dígitos (puede incluir +, espacios y guiones)."
            )
        self.__telefono = valor

    @property
    def empresa(self) -> Optional[str]:
        return self.__empresa

    # ──────────────────────────────────────────────────────
    # Implementación de EntidadSistema
    # ──────────────────────────────────────────────────────
    def obtener_id(self) -> str:
        return self.__cliente_id

    def describir(self) -> str:
        empresa_txt = f" | Empresa: {self.__empresa}" if self.__empresa else ""
        return (
            f"Cliente [{self.__cliente_id}] "
            f"Nombre: {self.__nombre} | "
            f"Email: {self.__email} | "
            f"Tel: {self.__telefono}"
            f"{empresa_txt}"
        )

    def validar(self) -> bool:
        """Verifica que todos los campos obligatorios estén presentes."""
        return all([
            bool(self.__cliente_id),
            bool(self.__nombre),
            bool(self.__email),
            bool(self.__telefono),
        ])

    # ──────────────────────────────────────────────────────
    # Gestión de clientes (lista interna de clase)
    # ──────────────────────────────────────────────────────
    _clientes: dict = {}   # {cliente_id: Cliente}

    @classmethod
    def registrar(cls, cliente: "Cliente") -> None:
        """Agrega el cliente al registro del sistema."""
        from excepciones import ClienteYaExisteError
        if cliente.cliente_id in cls._clientes:
            raise ClienteYaExisteError(cliente.cliente_id)
        cls._clientes[cliente.cliente_id] = cliente
        cls._logger.operacion(
            f"Registro de cliente '{cliente.cliente_id}'", "EXITOSO", "CLIENTE"
        )

    @classmethod
    def buscar(cls, cliente_id: str) -> "Cliente":
        """Busca y retorna un cliente por ID."""
        from excepciones import ClienteNoEncontradoError
        if cliente_id not in cls._clientes:
            raise ClienteNoEncontradoError(cliente_id)
        return cls._clientes[cliente_id]

    @classmethod
    def listar(cls) -> list:
        """Retorna la lista de todos los clientes registrados."""
        return list(cls._clientes.values())
