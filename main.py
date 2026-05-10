"""
main.py - Punto de entrada del Sistema Software FJ
Autor: Equipo Software FJ
Descripción: Simula al menos 10 operaciones completas que demuestran
             el uso de POO, excepciones personalizadas, manejo robusto
             de errores y el registro en logs.
"""

import sys
import os

# Asegurar que los módulos del proyecto se encuentren
sys.path.insert(0, os.path.dirname(__file__))

from cliente import Cliente
from excepciones import (
    ClienteError,
    ClienteYaExisteError,
    DatosClienteInvalidosError,
    DuracionInvalidaError,
    ParametroServicioInvalidoError,
    ReservaCanceladaError,
    ReservaYaConfirmadaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from logger import Logger
from reserva import EstadoReserva, Reserva
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala, Servicio

# ──────────────────────────────────────────────────────────────────────────────
SEPARADOR = "─" * 65
log = Logger()


def titulo(texto: str) -> None:
    print(f"\n{'═'*65}")
    print(f"  {texto}")
    print(f"{'═'*65}")


def subtitulo(numero: int, texto: str) -> None:
    print(f"\n{SEPARADOR}")
    print(f"  OP {numero:02d}: {texto}")
    print(SEPARADOR)


def ok(msg: str) -> None:
    print(f"  ✔  {msg}")


def err(msg: str) -> None:
    print(f"  ✘  {msg}")


def info(msg: str) -> None:
    print(f"  ℹ  {msg}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    titulo("SISTEMA INTEGRAL SOFTWARE FJ — SIMULACIÓN DE OPERACIONES")
    log.info("Inicio de simulación de operaciones", "MAIN")

    # ─────────────────────────────────────────────────────────────────────────
    # OP 01 — Registrar cliente válido
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(1, "Registrar cliente válido")
    try:
        c1 = Cliente("CLI-001", "Ana María Torres", "ana.torres@empresa.co",
                     "+57 310 456 7890", "Empresa ABC S.A.S")
        Cliente.registrar(c1)
        ok(c1.describir())
    except ClienteError as e:
        err(f"Error de cliente: {e}")
        log.error("OP01 fallida", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 02 — Registrar segundo cliente válido
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(2, "Registrar segundo cliente válido")
    try:
        c2 = Cliente("CLI-002", "Carlos Enrique Ruiz", "c.ruiz@tech.io",
                     "3001234567")
        Cliente.registrar(c2)
        ok(c2.describir())
    except ClienteError as e:
        err(f"Error de cliente: {e}")
        log.error("OP02 fallida", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 03 — Intentar registrar cliente con datos inválidos (email incorrecto)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(3, "Registrar cliente con email inválido (debe fallar)")
    try:
        c_invalido = Cliente("CLI-003", "Pedro Inválido", "correo-sin-arroba",
                             "3109876543")
        Cliente.registrar(c_invalido)
        ok(c_invalido.describir())
    except DatosClienteInvalidosError as e:
        err(f"[ESPERADO] Datos inválidos: {e}")
        log.error("OP03 — cliente con email inválido rechazado", "MAIN", e)
    except ClienteError as e:
        err(f"Error de cliente: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # OP 04 — Intentar registrar cliente duplicado
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(4, "Registrar cliente duplicado (debe fallar)")
    try:
        c_dup = Cliente("CLI-001", "Ana Duplicada", "ana2@otro.co", "3001111111")
        Cliente.registrar(c_dup)
    except ClienteYaExisteError as e:
        err(f"[ESPERADO] Cliente duplicado: {e}")
        log.error("OP04 — intento de duplicar cliente", "MAIN", e)
    except ClienteError as e:
        err(f"Error de cliente: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # OP 05 — Crear y registrar servicios válidos
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(5, "Crear y registrar tres servicios especializados")
    s1 = s2 = s3 = None
    try:
        s1 = ReservaSala("SRV-S01", "Sala Ejecutiva Norte", 80_000, capacidad_max=10)
        Servicio.registrar(s1)
        ok(s1.describir())

        s2 = AlquilerEquipo("SRV-E01", "Laptop HP ProBook", 25_000,
                            tipo_equipo="Laptop", deposito=200_000)
        Servicio.registrar(s2)
        ok(s2.describir())

        s3 = AsesoriaEspecializada("SRV-A01", "Asesoría Legal Corporativa",
                                    120_000, area="Derecho Empresarial",
                                    nivel_asesor="experto")
        Servicio.registrar(s3)
        ok(s3.describir())

    except (ParametroServicioInvalidoError, SoftwareFJError) as e:
        err(f"Error creando servicio: {e}")
        log.error("OP05 fallida", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 06 — Crear servicio con parámetro inválido (precio_hora negativo)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(6, "Crear servicio con precio negativo (debe fallar)")
    try:
        s_malo = ReservaSala("SRV-BAD", "Sala Fantasma", -5000, capacidad_max=5)
        Servicio.registrar(s_malo)
    except ParametroServicioInvalidoError as e:
        err(f"[ESPERADO] Parámetro inválido: {e}")
        log.error("OP06 — servicio con precio negativo rechazado", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 07 — Crear reserva válida y confirmarla (try/except/else)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(7, "Crear y confirmar reserva exitosa (3h, con IVA)")
    r1 = None
    if c1 and s1:
        try:
            r1 = Reserva(c1, s1, duracion_horas=3.0, aplicar_iva=True,
                         notas="Reunión de directivos Q3")
            Reserva.agregar(r1)
        except DuracionInvalidaError as e:
            err(f"Duración inválida: {e}")
            log.error("OP07a — duración inválida", "MAIN", e)
        except ServicioNoDisponibleError as e:
            err(f"Servicio no disponible: {e}")
        else:
            # Confirmar la reserva
            try:
                costo = r1.confirmar()
                ok(f"Reserva confirmada. Costo total: ${costo:,.0f} COP")
                info(r1.describir())
            except Exception as e:
                err(f"Error al confirmar: {e}")
                log.error("OP07b — error confirmando reserva", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 08 — Intentar confirmar la misma reserva dos veces
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(8, "Confirmar reserva ya confirmada (debe fallar)")
    if r1:
        try:
            r1.confirmar()
        except ReservaYaConfirmadaError as e:
            err(f"[ESPERADO] Doble confirmación: {e}")
            log.error("OP08 — intento de doble confirmación", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 09 — Crear reserva con duración inferior al mínimo (debe fallar)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(9, "Crear reserva con duración 0.2h (mínimo 0.5h) — debe fallar")
    if c2 and s2:
        try:
            r_corta = Reserva(c2, s2, duracion_horas=0.2)
            Reserva.agregar(r_corta)
            r_corta.confirmar()
        except DuracionInvalidaError as e:
            err(f"[ESPERADO] Duración insuficiente: {e}")
            log.error("OP09 — duración mínima no cumplida", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 10 — Reserva con descuento corporativo y procesamiento (try/finally)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(10, "Reserva con descuento corporativo + procesamiento completo")
    r2 = None
    if c2 and s3:
        try:
            r2 = Reserva(c2, s3, duracion_horas=2.0,
                         aplicar_descuento=True, aplicar_iva=True,
                         notas="Asesoría contrato internacional")
            Reserva.agregar(r2)
            costo = r2.confirmar()
            ok(f"Confirmada con descuento. Costo: ${costo:,.0f} COP")
            r2.procesar()
            ok(f"Reserva procesada. Estado: {r2.estado.value}")
            info(r2.describir())
        except SoftwareFJError as e:
            err(f"Error del sistema: {e}")
            log.error("OP10 fallida", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 11 — Intentar cancelar una reserva ya procesada (debe fallar)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(11, "Cancelar reserva procesada (debe fallar)")
    if r2 and r2.estado == EstadoReserva.PROCESADA:
        try:
            r2.cancelar("Prueba de cancelación inválida")
        except SoftwareFJError as e:
            err(f"[ESPERADO] No se puede cancelar: {e}")
            log.error("OP11 — intento de cancelar reserva procesada", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 12 — Servicio deshabilitado → intento de reserva (encadenamiento)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(12, "Reservar servicio deshabilitado (encadenamiento de excepción)")
    if s2 and c1:
        s2.disponible = False
        try:
            r_deshabilitada = Reserva(c1, s2, duracion_horas=1.0)
        except ServicioNoDisponibleError as e:
            try:
                # Simular encadenamiento: intentar buscar alternativa
                raise RuntimeError("No hay servicios de reemplazo disponibles") from e
            except RuntimeError as e_cadena:
                err(f"[ESPERADO] Encadenamiento: {e_cadena} | Causa: {e_cadena.__cause__}")
                log.error("OP12 — encadenamiento de excepción", "MAIN", e_cadena)
        finally:
            s2.disponible = True  # Restaurar para no afectar otras pruebas
            log.info("OP12 — servicio restaurado a disponible", "MAIN")

    # ─────────────────────────────────────────────────────────────────────────
    # OP 13 — Cálculo de costos polimórfico comparativo
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(13, "Comparar métodos de cálculo polimórfico (4h)")
    servicios_demo = [sv for sv in [s1, s2, s3] if sv]
    for sv in servicios_demo:
        try:
            base = sv.calcular_costo(4)
            con_iva = sv.calcular_costo_con_impuesto(4)
            con_dto = sv.calcular_costo_con_descuento(4, aplicar_iva=True)
            print(f"\n  {sv.nombre}")
            print(f"    Base              : ${base:>12,.0f} COP")
            print(f"    Con IVA (19%)     : ${con_iva:>12,.0f} COP")
            print(f"    Con Dto+IVA (10%) : ${con_dto:>12,.0f} COP")
        except SoftwareFJError as e:
            err(f"Error calculando costo para '{sv.nombre}': {e}")
            log.error(f"OP13 — error en cálculo {sv.nombre}", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # OP 14 — Cancelar una reserva pendiente (operación válida)
    # ─────────────────────────────────────────────────────────────────────────
    subtitulo(14, "Crear y cancelar reserva pendiente")
    if c1 and s1:
        try:
            r_cancelable = Reserva(c1, s1, duracion_horas=1.5, notas="Demo cancelación")
            Reserva.agregar(r_cancelable)
            r_cancelable.cancelar(motivo="Cambio de fecha solicitado por cliente")
            ok(f"Reserva cancelada. Estado: {r_cancelable.estado.value}")
            info(r_cancelable.describir())
        except SoftwareFJError as e:
            err(f"Error al cancelar: {e}")
            log.error("OP14 fallida", "MAIN", e)

    # ─────────────────────────────────────────────────────────────────────────
    # RESUMEN FINAL
    # ─────────────────────────────────────────────────────────────────────────
    titulo("RESUMEN DEL SISTEMA")
    print(f"\n  Clientes registrados : {len(Cliente.listar())}")
    print(f"  Servicios disponibles: {len(Servicio.listar())}")
    print(f"  Reservas totales     : {len(Reserva.listar())}")

    print("\n  Estado de reservas:")
    for r in Reserva.listar():
        print(f"    [{r.reserva_id}] {r.cliente.nombre:<25} "
              f"| {r.servicio.nombre:<30} "
              f"| {r.estado.value:<12}"
              f"| ${r.costo:>10,.0f} COP" if r.costo else
              f"    [{r.reserva_id}] {r.cliente.nombre:<25} "
              f"| {r.servicio.nombre:<30} "
              f"| {r.estado.value}")

    print(f"\n  Logs guardados en: logs.txt")
    log.info("Simulación completada exitosamente", "MAIN")
    print(f"\n{'═'*65}\n")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
