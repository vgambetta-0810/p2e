# CÓDIGO AGREGADO POR CODEX
"""Menú de consola para productos, proveedores y movimientos de stock."""
from decimal import Decimal, InvalidOperation

import conexion


class OperacionCancelada(Exception):
    """Señala que el usuario escribió cancelar en un campo."""


def pedir_input(etiqueta):
    valor = input(etiqueta)
    if valor.strip().casefold() == "cancelar":
        raise OperacionCancelada
    return valor.strip()


def pedir_entero(etiqueta, minimo=None):
    while True:
        try:
            valor = int(pedir_input(etiqueta))
            if minimo is not None and valor < minimo:
                print(f"Ingresá un número mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Ingresá un número entero válido.")


def pedir_texto(etiqueta, anterior=None):
    while True:
        valor = pedir_input(etiqueta)
        if anterior is not None and not valor:
            return anterior
        if valor:
            return valor
        print("El dato no puede quedar vacío.")


def pedir_precio(etiqueta="Precio: ", anterior=None):
    while True:
        entrada = pedir_input(etiqueta)
        if anterior is not None and not entrada:
            return anterior
        try:
            valor = Decimal(entrada.replace(",", "."))
            if valor.is_finite() and valor >= 0 and valor == valor.to_integral_value():
                return int(valor)
            print("El precio debe ser un entero no negativo (así está definido en MySQL).")
        except (InvalidOperation, ValueError):
            print("Ingresá un precio válido.")


def pedir_telefono(etiqueta, anterior=None):
    while True:
        entrada = pedir_input(etiqueta)
        if anterior is not None and not entrada:
            return anterior
        if entrada.isdigit():
            print("Aviso: MySQL guarda el teléfono como número; no conserva ceros iniciales ni el signo +.")
            return int(entrada)
        print("Ingresá solo dígitos, según el tipo entero de la columna cel.")


def pedir_perecedero(etiqueta="¿El producto es perecedero? 1. Sí  2. No: ", anterior=None):
    while True:
        opcion = pedir_input(etiqueta)
        if anterior is not None and not opcion:
            return anterior
        if opcion in ("1", "2"):
            return opcion == "1"
        print("Elegí 1 para Sí o 2 para No.")


def mostrar_producto(producto):
    producto.mostrar_datos()


def mostrar_proveedor(proveedor):
    print(f"ID: {proveedor.id} | Empresa: {proveedor.nombre} | Cel: {proveedor.nro} | Ubicación: {proveedor.ubicacion}")


def _cancelar():
    print("Operación cancelada; no se guardaron cambios.")


def menu_productos():
    while True:
        print("\nPRODUCTOS: 1 Crear  2 Listar  3 Buscar  4 Modificar  5 Eliminar  0 Volver")
        try:
            opcion = pedir_input("> ")
            if opcion == "1":
                nombre = pedir_texto("Nombre: ")
                marca = pedir_texto("Marca: ")
                perecedero = pedir_perecedero()
                id_proveedor = pedir_entero("ID del proveedor: ", 1)
                precio = pedir_precio()
                stock = pedir_entero("Stock inicial: ", 0)
                producto = conexion.crear_producto(nombre, precio, stock, id_proveedor, marca, perecedero)
                print("Producto registrado:")
                mostrar_producto(producto)
            elif opcion == "2":
                productos = conexion.listar_productos()
                if not productos:
                    print("No hay productos registrados.")
                for producto in productos:
                    mostrar_producto(producto)
            elif opcion == "3":
                producto = conexion.buscar_producto(pedir_entero("ID: ", 1))
                mostrar_producto(producto) if producto else print("No se encontró el producto.")
            elif opcion == "4":
                id_producto = pedir_entero("ID del producto: ", 1)
                anterior = conexion.buscar_producto(id_producto)
                if anterior is None:
                    print("No se encontró el producto.")
                    continue
                print("Dejá vacío cada campo que quieras conservar.")
                nombre = pedir_texto(f"Nombre [{anterior.nombre}]: ", anterior.nombre)
                marca = pedir_texto(f"Marca [{anterior.marca}]: ", anterior.marca)
                perecedero = pedir_perecedero("Perecedero 1-Sí / 2-No (vacío conserva): ", anterior.perecedero)
                precio = pedir_precio(f"Precio [{anterior.precio}]: ", anterior.precio)
                stock = pedir_entero(f"Stock [{anterior.stock}]: ", 0) if pedir_input("¿Modificar stock? (s/N): ").lower() == "s" else anterior.stock
                proveedor_id = pedir_entero(f"ID proveedor [{anterior.proveedor.id}]: ", 1) if pedir_input("¿Modificar proveedor? (s/N): ").lower() == "s" else anterior.proveedor.id
                producto = conexion.actualizar_producto(id_producto, nombre, precio, proveedor_id, marca, perecedero, stock)
                print("Producto actualizado.")
                mostrar_producto(producto)
            elif opcion == "5":
                id_producto = pedir_entero("ID del producto: ", 1)
                if conexion.buscar_producto(id_producto) is None:
                    print("No se encontró el producto.")
                elif pedir_input("¿Confirmás eliminarlo? (s/N): ").lower() == "s":
                    print("Producto eliminado." if conexion.eliminar_producto(id_producto) else "No se pudo eliminar.")
            elif opcion == "0":
                return
            else:
                print("Opción inválida.")
        except OperacionCancelada:
            _cancelar()
        except Exception as error:
            print("No se pudo completar la operación:", error)


def menu_proveedores():
    while True:
        print("\nPROVEEDORES: 1 Crear  2 Listar  3 Buscar y ver productos  4 Modificar  5 Eliminar  0 Volver")
        try:
            opcion = pedir_input("> ")
            if opcion == "1":
                proveedor = conexion.crear_proveedor(pedir_texto("Empresa: "), pedir_telefono("Celular/teléfono: "), pedir_texto("Ubicación: "))
                print("Proveedor registrado:")
                mostrar_proveedor(proveedor)
            elif opcion == "2":
                proveedores = conexion.listar_proveedores()
                if not proveedores:
                    print("No hay proveedores registrados.")
                for proveedor in proveedores:
                    mostrar_proveedor(proveedor)
            elif opcion == "3":
                id_proveedor = pedir_entero("ID: ", 1)
                proveedor = conexion.buscar_proveedor(id_proveedor)
                if not proveedor:
                    print("No se encontró el proveedor.")
                    continue
                mostrar_proveedor(proveedor)
                productos = conexion.productos_de_proveedor(id_proveedor)
                print("Productos asociados:")
                for producto in productos:
                    mostrar_producto(producto)
                if not productos:
                    print("No tiene productos asociados.")
            elif opcion == "4":
                id_proveedor = pedir_entero("ID: ", 1)
                anterior = conexion.buscar_proveedor(id_proveedor)
                if anterior is None:
                    print("No se encontró el proveedor.")
                    continue
                print("Dejá vacío cada campo que quieras conservar.")
                proveedor = conexion.actualizar_proveedor(
                    id_proveedor,
                    pedir_texto(f"Empresa [{anterior.nombre}]: ", anterior.nombre),
                    pedir_telefono(f"Teléfono [{anterior.nro}]: ", anterior.nro),
                    pedir_texto(f"Ubicación [{anterior.ubicacion}]: ", anterior.ubicacion))
                print("Proveedor actualizado.")
                mostrar_proveedor(proveedor)
            elif opcion == "5":
                id_proveedor = pedir_entero("ID: ", 1)
                if conexion.buscar_proveedor(id_proveedor) is None:
                    print("No se encontró el proveedor.")
                elif pedir_input("¿Confirmás eliminarlo? (s/N): ").lower() == "s":
                    print("Proveedor eliminado." if conexion.eliminar_proveedor(id_proveedor) else "No se pudo eliminar.")
            elif opcion == "0":
                return
            else:
                print("Opción inválida.")
        except OperacionCancelada:
            _cancelar()
        except Exception as error:
            print("No se pudo completar la operación:", error)


def menu_movimientos():
    while True:
        print("\nMOVIMIENTOS: 1 Registrar entrada  2 Registrar salida  3 Historial  4 Por producto  0 Volver")
        try:
            opcion = pedir_input("> ")
            if opcion in ("1", "2"):
                id_producto = pedir_entero("ID del producto: ", 1)
                cantidad = pedir_entero("Cantidad: ", 1)
                tipo = "ENTRADA" if opcion == "1" else "SALIDA"
                movimiento, producto = conexion.registrar_movimiento(id_producto, cantidad, tipo)
                movimiento.registrar_mov()
                print(f"Stock actualizado: {producto.stock}")
            elif opcion in ("3", "4"):
                id_producto = pedir_entero("ID del producto: ", 1) if opcion == "4" else None
                movimientos = conexion.listar_movimientos(id_producto)
                if not movimientos:
                    print("Todavía no hay movimientos registrados.")
                for item in movimientos:
                    print(f"Movimiento {item['idmov']} | Producto {item['producto_id']} - {item['nombre_producto']} | {item['tipo_mov']} | Cantidad: {item['cantidad']} | {item['fecha_hora']}")
            elif opcion == "0":
                return
            else:
                print("Opción inválida.")
        except OperacionCancelada:
            _cancelar()
        except Exception as error:
            print("No se pudo completar la operación:", error)


def main():
    while True:
        print("\nMINIMERCADO: 1 Productos  2 Proveedores  3 Movimientos de stock  0 Salir")
        try:
            opcion = pedir_input("> ")
            if opcion == "1":
                menu_productos()
            elif opcion == "2":
                menu_proveedores()
            elif opcion == "3":
                menu_movimientos()
            elif opcion == "0":
                print("Hasta luego.")
                return
            else:
                print("Opción inválida.")
        except OperacionCancelada:
            _cancelar()


if __name__ == "__main__":
    main()
