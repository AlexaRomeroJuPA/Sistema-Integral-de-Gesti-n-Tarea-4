"""
main.py - Punto de entrada del Sistema Software FJ
Autor: Equipo Software FJ
Descripción: Menú interactivo que permite al usuario gestionar clientes,
             servicios y reservas, con manejo robusto de excepciones.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from cliente import Cliente
from excepciones import (
    ClienteError, ClienteYaExisteError, DatosClienteInvalidosError,
    DuracionInvalidaError, ParametroServicioInvalidoError,
    ReservaCanceladaError, ReservaYaConfirmadaError,
    ServicioNoDisponibleError, SoftwareFJError,
)
from logger import Logger
from reserva import EstadoReserva, Reserva
from servicio import AlquilerEquipo, AsesoriaEspecializada, ReservaSala, Servicio

log = Logger()
SEP = "─" * 55


def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n  Presiona Enter para continuar...")


def titulo(texto):
    print(f"\n{'═'*55}")
    print(f"   {texto}")
    print(f"{'═'*55}")


def ok(msg): print(f"\n  ✔  {msg}")
def err(msg): print(f"\n  ✘  {msg}")
def info(msg): print(f"  ℹ  {msg}")


# ══════════════════════════════════════════════════════
# MÓDULO: CLIENTES
# ══════════════════════════════════════════════════════

def menu_clientes():
    while True:
        titulo("GESTIÓN DE CLIENTES")
        print("  1. Registrar nuevo cliente")
        print("  2. Buscar cliente por ID")
        print("  3. Listar todos los clientes")
        print("  0. Volver al menú principal")
        opcion = input("\n  Elige una opción: ").strip()
        if opcion == "1":
            registrar_cliente()
        elif opcion == "2":
            buscar_cliente()
        elif opcion == "3":
            listar_clientes()
        elif opcion == "0":
            break
        else:
            err("Opción inválida.")
        pausar()


def registrar_cliente():
    titulo("REGISTRAR CLIENTE")
    try:
        cid      = input("  ID del cliente (ej: CLI-003): ").strip()
        nombre   = input("  Nombre completo            : ").strip()
        email    = input("  Correo electrónico         : ").strip()
        telefono = input("  Teléfono                   : ").strip()
        empresa  = input("  Empresa (opcional)         : ").strip()
        c = Cliente(cid, nombre, email, telefono, empresa if empresa else None)
        Cliente.registrar(c)
        ok(f"Cliente '{nombre}' registrado exitosamente.")
        info(c.describir())
        log.operacion(f"Registro cliente {cid}", "EXITOSO", "MAIN")
    except ClienteYaExisteError as e:
        err(f"[ESPERADO] {e}")
        log.error("Cliente duplicado", "MAIN", e)
    except DatosClienteInvalidosError as e:
        err(f"[ESPERADO] Dato inválido: {e}")
        log.error("Datos inválidos", "MAIN", e)
    except ClienteError as e:
        err(f"Error de cliente: {e}")
        log.error("Error cliente", "MAIN", e)


def buscar_cliente():
    titulo("BUSCAR CLIENTE")
    cid = input("  ID del cliente a buscar: ").strip()
    try:
        c = Cliente.buscar(cid)
        ok("Cliente encontrado:")
        info(c.describir())
    except SoftwareFJError as e:
        err(str(e))
        log.error("Búsqueda fallida", "MAIN", e)


def listar_clientes():
    titulo("LISTA DE CLIENTES")
    clientes = Cliente.listar()
    if not clientes:
        info("No hay clientes registrados.")
        return
    for c in clientes:
        print(f"  • {c.describir()}")


# ══════════════════════════════════════════════════════
# MÓDULO: SERVICIOS
# ══════════════════════════════════════════════════════

def menu_servicios():
    while True:
        titulo("GESTIÓN DE SERVICIOS")
        print("  1. Crear Reserva de Sala")
        print("  2. Crear Alquiler de Equipo")
        print("  3. Crear Asesoría Especializada")
        print("  4. Listar todos los servicios")
        print("  5. Habilitar / Deshabilitar servicio")
        print("  0. Volver al menú principal")
        opcion = input("\n  Elige una opción: ").strip()
        if opcion == "1":
            crear_sala()
        elif opcion == "2":
            crear_equipo()
        elif opcion == "3":
            crear_asesoria()
        elif opcion == "4":
            listar_servicios()
        elif opcion == "5":
            toggle_servicio()
        elif opcion == "0":
            break
        else:
            err("Opción inválida.")
        pausar()


def crear_sala():
    titulo("CREAR RESERVA DE SALA")
    try:
        sid    = input("  ID del servicio (ej: SRV-S01): ").strip()
        nombre = input("  Nombre de la sala             : ").strip()
        precio = float(input("  Precio por hora (COP)         : ").strip())
        cap    = int(input("  Capacidad máxima (personas)   : ").strip())
        s = ReservaSala(sid, nombre, precio, cap)
        Servicio.registrar(s)
        ok(f"Sala '{nombre}' registrada.")
        info(s.describir())
    except (ValueError, ParametroServicioInvalidoError, SoftwareFJError) as e:
        err(f"Error: {e}")
        log.error("Error creando sala", "MAIN", e)


def crear_equipo():
    titulo("CREAR ALQUILER DE EQUIPO")
    try:
        sid     = input("  ID del servicio (ej: SRV-E01): ").strip()
        nombre  = input("  Nombre del equipo             : ").strip()
        precio  = float(input("  Precio por hora (COP)         : ").strip())
        tipo    = input("  Tipo de equipo                : ").strip()
        dep_txt = input("  Depósito requerido (COP, 0=no): ").strip()
        deposito = float(dep_txt) if dep_txt else 0.0
        s = AlquilerEquipo(sid, nombre, precio, tipo, deposito > 0, deposito)
        Servicio.registrar(s)
        ok(f"Equipo '{nombre}' registrado.")
        info(s.describir())
    except (ValueError, ParametroServicioInvalidoError, SoftwareFJError) as e:
        err(f"Error: {e}")
        log.error("Error creando equipo", "MAIN", e)


def crear_asesoria():
    titulo("CREAR ASESORÍA ESPECIALIZADA")
    try:
        sid    = input("  ID del servicio (ej: SRV-A01) : ").strip()
        nombre = input("  Nombre de la asesoría          : ").strip()
        precio = float(input("  Precio base por hora (COP)    : ").strip())
        area   = input("  Área de especialización        : ").strip()
        print("  Niveles disponibles: junior | senior | experto")
        nivel  = input("  Nivel del asesor               : ").strip()
        s = AsesoriaEspecializada(sid, nombre, precio, area, nivel)
        Servicio.registrar(s)
        ok(f"Asesoría '{nombre}' registrada.")
        info(s.describir())
    except (ValueError, ParametroServicioInvalidoError, SoftwareFJError) as e:
        err(f"Error: {e}")
        log.error("Error creando asesoría", "MAIN", e)


def listar_servicios():
    titulo("LISTA DE SERVICIOS")
    servicios = Servicio.listar()
    if not servicios:
        info("No hay servicios registrados.")
        return
    for s in servicios:
        print(f"  • {s.describir()}")


def toggle_servicio():
    titulo("HABILITAR / DESHABILITAR SERVICIO")
    listar_servicios()
    sid = input("\n  ID del servicio: ").strip()
    try:
        s = Servicio.buscar(sid)
        s.disponible = not s.disponible
        estado = "habilitado" if s.disponible else "deshabilitado"
        ok(f"Servicio '{s.nombre}' {estado}.")
        log.operacion(f"Toggle {sid}", estado.upper(), "MAIN")
    except SoftwareFJError as e:
        err(str(e))
        log.error("Error toggle servicio", "MAIN", e)


# ══════════════════════════════════════════════════════
# MÓDULO: RESERVAS
# ══════════════════════════════════════════════════════

def menu_reservas():
    while True:
        titulo("GESTIÓN DE RESERVAS")
        print("  1. Crear nueva reserva")
        print("  2. Confirmar reserva")
        print("  3. Procesar reserva")
        print("  4. Cancelar reserva")
        print("  5. Listar todas las reservas")
        print("  6. Ver detalle de una reserva")
        print("  0. Volver al menú principal")
        opcion = input("\n  Elige una opción: ").strip()
        if opcion == "1":
            crear_reserva()
        elif opcion == "2":
            confirmar_reserva()
        elif opcion == "3":
            procesar_reserva()
        elif opcion == "4":
            cancelar_reserva()
        elif opcion == "5":
            listar_reservas()
        elif opcion == "6":
            detalle_reserva()
        elif opcion == "0":
            break
        else:
            err("Opción inválida.")
        pausar()


def crear_reserva():
    titulo("CREAR RESERVA")
    listar_clientes()
    cid = input("\n  ID del cliente  : ").strip()
    listar_servicios()
    sid = input("\n  ID del servicio : ").strip()
    try:
        cliente  = Cliente.buscar(cid)
        servicio = Servicio.buscar(sid)
        horas    = float(input("  Duración (horas): ").strip())
        notas    = input("  Notas (opcional): ").strip()
        desc     = input("  ¿Aplicar descuento corporativo 10%? (s/n): ").strip().lower() == "s"
        iva      = input("  ¿Aplicar IVA 19%? (s/n): ").strip().lower() == "s"
        r = Reserva(cliente, servicio, horas,
                    notas if notas else None,
                    aplicar_descuento=desc, aplicar_iva=iva)
        Reserva.agregar(r)
        ok(f"Reserva creada con ID: {r.reserva_id}")
        info(r.describir())
    except DuracionInvalidaError as e:
        err(f"[ESPERADO] {e}")
        log.error("Duración inválida", "MAIN", e)
    except ServicioNoDisponibleError as e:
        err(f"[ESPERADO] {e}")
        log.error("Servicio no disponible", "MAIN", e)
    except (ValueError, SoftwareFJError) as e:
        err(f"Error: {e}")
        log.error("Error creando reserva", "MAIN", e)


def confirmar_reserva():
    titulo("CONFIRMAR RESERVA")
    listar_reservas()
    rid = input("\n  ID de la reserva: ").strip().upper()
    try:
        r = Reserva.buscar(rid)
        costo = r.confirmar()
        ok(f"Reserva confirmada. Costo total: ${costo:,.0f} COP")
        info(r.describir())
    except ReservaYaConfirmadaError as e:
        err(f"[ESPERADO] {e}")
        log.error("Doble confirmación", "MAIN", e)
    except ReservaCanceladaError as e:
        err(f"[ESPERADO] {e}")
        log.error("Confirmar cancelada", "MAIN", e)
    except SoftwareFJError as e:
        err(str(e))
        log.error("Error confirmando", "MAIN", e)


def procesar_reserva():
    titulo("PROCESAR RESERVA")
    listar_reservas()
    rid = input("\n  ID de la reserva: ").strip().upper()
    try:
        r = Reserva.buscar(rid)
        r.procesar()
        ok(f"Reserva procesada. Estado: {r.estado.value}")
    except SoftwareFJError as e:
        err(str(e))
        log.error("Error procesando", "MAIN", e)


def cancelar_reserva():
    titulo("CANCELAR RESERVA")
    listar_reservas()
    rid    = input("\n  ID de la reserva: ").strip().upper()
    motivo = input("  Motivo de cancelación: ").strip()
    try:
        r = Reserva.buscar(rid)
        r.cancelar(motivo if motivo else "Sin especificar")
        ok("Reserva cancelada exitosamente.")
        info(r.describir())
    except SoftwareFJError as e:
        err(str(e))
        log.error("Error cancelando", "MAIN", e)


def listar_reservas():
    titulo("LISTA DE RESERVAS")
    reservas = Reserva.listar()
    if not reservas:
        info("No hay reservas registradas.")
        return
    print(f"  {'ID':<10} {'Cliente':<22} {'Servicio':<22} {'Estado':<12} {'Costo'}")
    print(f"  {SEP}")
    for r in reservas:
        costo = f"${r.costo:>10,.0f}" if r.costo else "  Pendiente"
        print(f"  {r.reserva_id:<10} {r.cliente.nombre:<22} "
              f"{r.servicio.nombre:<22} {r.estado.value:<12} {costo}")


def detalle_reserva():
    titulo("DETALLE DE RESERVA")
    rid = input("  ID de la reserva: ").strip().upper()
    try:
        r = Reserva.buscar(rid)
        print()
        print(r.describir())
    except SoftwareFJError as e:
        err(str(e))


# ══════════════════════════════════════════════════════
# MÓDULO: DEMO AUTOMÁTICA
# ══════════════════════════════════════════════════════

def ejecutar_demo():
    titulo("SIMULACIÓN DEMO — 10 OPERACIONES")
    print("  Ejecutando operaciones de prueba...\n")

    def op(codigo, desc, accion):
        print(f"\n  {SEP}")
        print(f"  {codigo}: {desc}")
        try:
            accion()
            ok("Operación exitosa")
        except (DatosClienteInvalidosError, ParametroServicioInvalidoError,
                DuracionInvalidaError, SoftwareFJError) as e:
            err(f"[CONTROLADO] {type(e).__name__}: {e}")
            log.error(f"{codigo}", "DEMO", e)

    op("OP01", "Registrar cliente válido",
       lambda: Cliente.registrar(
           Cliente("DEMO-01", "Ana Torres Demo", "ana.demo@empresa.co", "3101234567")))

    op("OP02", "Registrar segundo cliente válido",
       lambda: Cliente.registrar(
           Cliente("DEMO-02", "Luis Pérez Demo", "luis.demo@tech.io", "3209876543")))

    op("OP03", "Registrar cliente con email inválido (debe fallar)",
       lambda: Cliente.registrar(
           Cliente("DEMO-03", "Error Demo", "correo-invalido", "3001111111")))

    op("OP04", "Crear servicio ReservaSala",
       lambda: Servicio.registrar(
           ReservaSala("DEMO-S1", "Sala Demo Norte", 80000, 10)))

    op("OP05", "Crear servicio AlquilerEquipo",
       lambda: Servicio.registrar(
           AlquilerEquipo("DEMO-E1", "Laptop Demo", 25000, "Laptop", True, 150000)))

    op("OP06", "Crear servicio AsesoriaEspecializada",
       lambda: Servicio.registrar(
           AsesoriaEspecializada("DEMO-A1", "Asesoría Demo", 100000, "Legal", "experto")))

    op("OP07", "Crear servicio con precio negativo (debe fallar)",
       lambda: Servicio.registrar(
           ReservaSala("DEMO-BAD", "Sala Mala", -1000, 5)))

    def reserva_exitosa():
        c = Cliente.buscar("DEMO-01")
        s = Servicio.buscar("DEMO-S1")
        r = Reserva(c, s, 2.0, aplicar_iva=True)
        Reserva.agregar(r)
        costo = r.confirmar()
        info(f"    Reserva {r.reserva_id} confirmada. Costo: ${costo:,.0f} COP")

    op("OP08", "Crear y confirmar reserva exitosa", reserva_exitosa)

    op("OP09", "Reserva con duración inválida 0.1h (debe fallar)",
       lambda: Reserva(Cliente.buscar("DEMO-01"),
                       Servicio.buscar("DEMO-S1"), 0.1))

    def reserva_descuento():
        c = Cliente.buscar("DEMO-02")
        s = Servicio.buscar("DEMO-A1")
        r = Reserva(c, s, 3.0, aplicar_descuento=True, aplicar_iva=True)
        Reserva.agregar(r)
        costo = r.confirmar()
        r.procesar()
        info(f"    Reserva {r.reserva_id} procesada. Costo: ${costo:,.0f} COP")

    op("OP10", "Reserva con descuento + procesamiento completo", reserva_descuento)

    print(f"\n  {SEP}")
    ok("Demo completada. Puedes ver los datos en el menú principal.")
    log.info("Demo completada", "MAIN")


# ══════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════

def resumen():
    titulo("RESUMEN DEL SISTEMA")
    print(f"  Clientes registrados : {len(Cliente.listar())}")
    print(f"  Servicios disponibles: {len(Servicio.listar())}")
    print(f"  Reservas totales     : {len(Reserva.listar())}")
    pausar()


def main():
    log.info("Sistema iniciado", "MAIN")
    while True:
        limpiar()
        titulo("SOFTWARE FJ — SISTEMA DE GESTIÓN")
        print("  1. Gestión de Clientes")
        print("  2. Gestión de Servicios")
        print("  3. Gestión de Reservas")
        print("  4. Ejecutar Simulación Demo (10 ops)")
        print("  5. Ver Resumen del Sistema")
        print("  0. Salir")
        print(f"\n  {SEP}")
        opcion = input("  Elige una opción: ").strip()

        if opcion == "1":
            menu_clientes()
        elif opcion == "2":
            menu_servicios()
        elif opcion == "3":
            menu_reservas()
        elif opcion == "4":
            ejecutar_demo()
            pausar()
        elif opcion == "5":
            resumen()
        elif opcion == "0":
            titulo("¡Hasta luego! — Software FJ")
            log.info("Sistema cerrado", "MAIN")
            sys.exit(0)
        else:
            err("Opción inválida, intenta de nuevo.")
            pausar()


if __name__ == "__main__":
    main()
