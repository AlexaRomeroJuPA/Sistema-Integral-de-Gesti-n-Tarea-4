"""
excepciones.py - Excepciones personalizadas del Sistema Software FJ
Autor: Equipo Software FJ
Descripción: Define todas las excepciones personalizadas del sistema.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "SFJ-000"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


# ──────────────────── EXCEPCIONES DE CLIENTE ────────────────────

class ClienteError(SoftwareFJError):
    """Error base relacionado con clientes."""
    def __init__(self, mensaje: str, codigo: str = "CLI-001"):
        super().__init__(mensaje, codigo)


class ClienteYaExisteError(ClienteError):
    """Se intenta registrar un cliente con ID ya existente."""
    def __init__(self, cliente_id: str):
        super().__init__(
            f"El cliente con ID '{cliente_id}' ya está registrado.",
            "CLI-002"
        )


class ClienteNoEncontradoError(ClienteError):
    """No se encuentra el cliente solicitado."""
    def __init__(self, cliente_id: str):
        super().__init__(
            f"No se encontró ningún cliente con ID '{cliente_id}'.",
            "CLI-003"
        )


class DatosClienteInvalidosError(ClienteError):
    """Los datos del cliente no cumplen las validaciones."""
    def __init__(self, campo: str, valor: str, razon: str):
        super().__init__(
            f"Dato inválido en campo '{campo}' con valor '{valor}': {razon}",
            "CLI-004"
        )


# ──────────────────── EXCEPCIONES DE SERVICIO ────────────────────

class ServicioError(SoftwareFJError):
    """Error base relacionado con servicios."""
    def __init__(self, mensaje: str, codigo: str = "SRV-001"):
        super().__init__(mensaje, codigo)


class ServicioNoDisponibleError(ServicioError):
    """El servicio solicitado no está disponible."""
    def __init__(self, nombre_servicio: str):
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible en este momento.",
            "SRV-002"
        )


class ServicioNoEncontradoError(ServicioError):
    """No se encuentra el servicio solicitado."""
    def __init__(self, servicio_id: str):
        super().__init__(
            f"No se encontró el servicio con ID '{servicio_id}'.",
            "SRV-003"
        )


class ParametroServicioInvalidoError(ServicioError):
    """Parámetro inválido para configurar o usar el servicio."""
    def __init__(self, parametro: str, valor, razon: str):
        super().__init__(
            f"Parámetro inválido '{parametro}' = '{valor}': {razon}",
            "SRV-004"
        )


class CapacidadExcedidaError(ServicioError):
    """Se supera la capacidad máxima del servicio."""
    def __init__(self, servicio: str, capacidad_max: int):
        super().__init__(
            f"El servicio '{servicio}' tiene capacidad máxima de {capacidad_max} personas.",
            "SRV-005"
        )


# ──────────────────── EXCEPCIONES DE RESERVA ────────────────────

class ReservaError(SoftwareFJError):
    """Error base relacionado con reservas."""
    def __init__(self, mensaje: str, codigo: str = "RES-001"):
        super().__init__(mensaje, codigo)


class ReservaNoEncontradaError(ReservaError):
    """No se encuentra la reserva solicitada."""
    def __init__(self, reserva_id: str):
        super().__init__(
            f"No se encontró la reserva con ID '{reserva_id}'.",
            "RES-002"
        )


class ReservaYaConfirmadaError(ReservaError):
    """Se intenta confirmar una reserva ya confirmada."""
    def __init__(self, reserva_id: str):
        super().__init__(
            f"La reserva '{reserva_id}' ya fue confirmada anteriormente.",
            "RES-003"
        )


class ReservaCanceladaError(ReservaError):
    """Se intenta operar sobre una reserva cancelada."""
    def __init__(self, reserva_id: str):
        super().__init__(
            f"La reserva '{reserva_id}' está cancelada y no puede modificarse.",
            "RES-004"
        )


class DuracionInvalidaError(ReservaError):
    """La duración especificada no es válida."""
    def __init__(self, duracion: float, minimo: float = 0.5):
        super().__init__(
            f"Duración '{duracion}h' inválida. El mínimo permitido es {minimo}h.",
            "RES-005"
        )


class CostoInsuficienteError(ReservaError):
    """El costo calculado es inconsistente o insuficiente."""
    def __init__(self, costo: float):
        super().__init__(
            f"El costo calculado '{costo}' es inconsistente con los parámetros del servicio.",
            "RES-006"
        )
