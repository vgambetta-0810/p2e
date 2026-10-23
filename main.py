# CÓDIGO AGREGADO POR CODEX
"""Menú de consola para los CRUD de productos y proveedores."""
from decimal import Decimal, InvalidOperation

import conexion
from poo import Producto


def pedir_entero(etiqueta, minimo=None):
    while True:
        try:
            valor = int(input(etiqueta))
            if minimo is not None and valor < minimo:
                print(f"Ingresá un número mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Ingresá un número entero válido.")


def pedir_texto(etiqueta):
    while True:
        valor = input(etiqueta).strip()
        if valor:
            return valor
        print("El dato no puede quedar vacío.")


def pedir_precio(etiqueta="Precio: "):
    while True:
        try:
            valor = Decimal(input(etiqueta).replace(",", "."))
            if valor.is_finite() and valor >= 0 and valor == valor.to_integral_value():
                return int(valor)
            print("El precio debe ser un entero no negativo (así está definido en MySQL).")
        except (InvalidOperation, ValueError):
            print("Ingresá un precio válido.")


def pedir_telefono(etiqueta):
    while True:
        valor = input(etiqueta).strip()
        if valor.isdigit():
            print("Aviso: MySQL guarda el teléfono como número; no conserva ceros iniciales ni el signo +.")
            return int(valor)
        print("Ingresá solo dígitos, según el tipo entero de la columna cel.")


def mostrar_producto(producto):
    producto.mostrar_datos()


def mostrar_proveedor(proveedor):
    print(f"ID: {proveedor.id} | Empresa: {proveedor.nombre} | Cel: {proveedor.nro} | Ubicación: {proveedor.ubicacion}")


def menu_productos():
    while True:
        print("\nPRODUCTOS: 1 Crear  2 Listar  3 Buscar  4 Modificar  5 Eliminar  6 Stock  0 Volver")
        opcion = input("> ").strip()
        try:
            if opcion == "1":
                nombre = pedir_texto("Nombre: ")
                precio = pedir_precio()
                stock = pedir_entero("Stock inicial: ", 0)
                id_proveedor = pedir_entero("ID del proveedor: ", 1)
                p = conexion.crear_producto(nombre, precio, stock, id_proveedor)
                print("Producto registrado:")
                mostrar_producto(p)
            elif opcion == "2":
                productos = conexion.listar_productos()
                if not productos:
                    print("No hay productos registrados.")
                for p in productos:
                    mostrar_producto(p)
            elif opcion == "3":
                p = conexion.buscar_producto(pedir_entero("ID: ", 1))
                mostrar_producto(p) if p else print("No se encontró el producto.")
            elif opcion == "4":
                id_p = pedir_entero("ID del producto: ", 1)
                if conexion.buscar_producto(id_p) is None:
                    print("No se encontró el producto.")
                    continue
                p = conexion.actualizar_producto(id_p, pedir_texto("Nombre nuevo: "), pedir_precio("Precio nuevo: "), pedir_entero("ID del proveedor: ", 1))
                print("Producto actualizado.")
                mostrar_producto(p)
            elif opcion == "5":
                id_p = pedir_entero("ID del producto: ", 1)
                if conexion.buscar_producto(id_p) is None:
                    print("No se encontró el producto.")
                elif input("¿Confirmás eliminarlo? (s/N): ").strip().lower() == "s":
                    print("Producto eliminado." if conexion.eliminar_producto(id_p) else "No se pudo eliminar.")
            elif opcion == "6":
                id_p = pedir_entero("ID del producto: ", 1)
                cantidad = pedir_entero("Cantidad: ", 1)
                tipo = input("Aumentar o disminuir (a/d): ").strip().lower()
                if tipo not in ("a", "d"):
                    print("Opción inválida.")
                    continue
                p = conexion.cambiar_stock(id_p, cantidad, tipo == "a")
                if p:
                    print("Stock actualizado en MySQL:")
                    mostrar_producto(p)
                else:
                    print("No se encontró el producto.")
            elif opcion == "0":
                return
            else:
                print("Opción inválida.")
        except Exception as error:
            print("No se pudo completar la operación:", error)


def menu_proveedores():
    while True:
        print("\nPROVEEDORES: 1 Crear  2 Listar  3 Buscar y ver productos  4 Modificar  5 Eliminar  0 Volver")
        opcion = input("> ").strip()
        try:
            if opcion == "1":
                p = conexion.crear_proveedor(pedir_texto("Empresa: "), pedir_telefono("Celular/teléfono: "), pedir_texto("Ubicación: "))
                print("Proveedor registrado:")
                mostrar_proveedor(p)
            elif opcion == "2":
                proveedores = conexion.listar_proveedores()
                if not proveedores:
                    print("No hay proveedores registrados.")
                for p in proveedores:
                    mostrar_proveedor(p)
            elif opcion == "3":
                id_p = pedir_entero("ID: ", 1)
                p = conexion.buscar_proveedor(id_p)
                if not p:
                    print("No se encontró el proveedor.")
                    continue
                mostrar_proveedor(p)
                productos = conexion.productos_de_proveedor(id_p)
                p.productos = productos
                print("Productos asociados:")
                for producto in productos:
                    mostrar_producto(producto)
                if not productos:
                    print("No tiene productos asociados.")
            elif opcion == "4":
                id_p = pedir_entero("ID: ", 1)
                if conexion.buscar_proveedor(id_p) is None:
                    print("No se encontró el proveedor.")
                    continue
                p = conexion.actualizar_proveedor(id_p, pedir_texto("Empresa nueva: "), pedir_telefono("Teléfono nuevo: "), pedir_texto("Ubicación nueva: "))
                print("Proveedor actualizado.")
                mostrar_proveedor(p)
            elif opcion == "5":
                id_p = pedir_entero("ID: ", 1)
                if conexion.buscar_proveedor(id_p) is None:
                    print("No se encontró el proveedor.")
                elif input("¿Confirmás eliminarlo? (s/N): ").strip().lower() == "s":
                    print("Proveedor eliminado." if conexion.eliminar_proveedor(id_p) else "No se pudo eliminar.")
            elif opcion == "0":
                return
            else:
                print("Opción inválida.")
        except Exception as error:
            print("No se pudo completar la operación:", error)


def main():
    while True:
        print("\nMINIMERCADO: 1 Productos  2 Proveedores  0 Salir")
        opcion = input("> ").strip()
        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_proveedores()
        elif opcion == "0":
            print("Hasta luego.")
            return
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
