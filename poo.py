# ===== CÓDIGO ORIGINAL DEL GRUPO =====
# Se conservaron las clases, sus nombres principales, atributos y métodos
# iniciados por el grupo. Las correcciones y agregados están marcados debajo.
# ===== FIN CÓDIGO ORIGINAL DEL GRUPO =====

# ===== CORRECCIÓN DE CODEX =====
from datetime import datetime
from decimal import Decimal, InvalidOperation
# ===== FIN CORRECCIÓN DE CODEX =====


class Usuario:
    def __init__(self, DNI, nombre, apellido, NRO, mail):
        self.dni = DNI
        self.nombre = nombre
        self.apellido = apellido
        self.nro = NRO
        self.mail = mail

    def iniciar_sesion(self):
        print("Iniciando sesión :) ")

    def cerrar_sesion(self):
        print("Cerrando sesión :( ")


class Producto:
    # CÓDIGO AGREGADO POR CODEX: validación de datos y encapsulamiento del stock.
    def __init__(self, codigo, nombre, precio: float, stock: int,
                 marca="No informada", proveedor=None, perecedero=False):
        if codigo is None or not str(codigo).strip():
            raise ValueError("El código del producto no puede quedar vacío.")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del producto no puede quedar vacío.")
        try:
            precio_validado = Decimal(str(precio))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("El precio debe ser un número válido.") from exc
        if not precio_validado.is_finite() or precio_validado < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.codigo = codigo
        self.nombre = nombre.strip()
        self.precio = float(precio_validado)
        self._stock = self._validar_stock_inicial(stock)
        self.marca = marca
        self.proveedor = proveedor
        self.perecedero = bool(perecedero)

    def mostrar_datos(self):
        proveedor = getattr(self.proveedor, "nombre", self.proveedor)
        print(
            f"Código: {self.codigo} | Nombre: {self.nombre} | "
            f"Precio: ${self.precio:.2f} | Stock: {self.consultar_stock()} | "
            f"Marca: {self.marca} | Proveedor: {proveedor} | "
            f"Perecedero: {self.perecedero}"
        )

    def consultar_stock(self):
        return self._stock

    @property
    def stock(self):
        return self._stock

    @staticmethod
    def _validar_stock_inicial(stock):
        if isinstance(stock, bool) or not isinstance(stock, int) or not 0 <= stock <= 2147483647:
            raise ValueError("El stock debe ser un entero entre 0 y 2147483647.")
        return stock

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que cero.")

    def aumentar_stock(self, cantidad):
        self._validar_cantidad(cantidad)
        if self._stock + cantidad > 2147483647:
            raise ValueError("El stock supera el máximo permitido por la columna INT de MySQL.")
        self._stock += cantidad
        return self._stock

    def disminuir_stock(self, cantidad):
        self._validar_cantidad(cantidad)
        if cantidad > self._stock:
            return False
        self._stock -= cantidad
        return self._stock

    def actualizar_stock(self, stock):
        # Compatibilidad con el método anterior: actualiza solo a un entero no negativo.
        nuevo = self._validar_stock_inicial(stock)
        self._stock = nuevo
        return self._stock

    def esta_disponible(self):
        disponible = self.stock > 0
        print("El producto sí está disponible" if disponible
              else "El producto no está disponible")
        return disponible


class Proveedor:
    # CÓDIGO AGREGADO POR CODEX: mantiene la interfaz original y permite cargar productos desde MySQL.
    def __init__(self, id, nombre, ubicacion, nro):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.nro = nro
        self.productos = []

    def actualizar_datos(self, nombre=None, ubicacion=None, nro=None):
        if nombre is None and ubicacion is None and nro is None:
            from main import OperacionCancelada, pedir_input
            try:
                dato = pedir_input("Seleccione 1 nombre, 2 ubicación o 3 teléfono: ")
            except OperacionCancelada:
                print("Operación cancelada; no se guardaron cambios.")
                return False
            if dato == "1":
                try:
                    nombre = pedir_input("Ingrese el nombre nuevo del proveedor: ")
                except OperacionCancelada:
                    print("Operación cancelada; no se guardaron cambios.")
                    return False
            elif dato == "2":
                try:
                    ubicacion = pedir_input("Ingrese la ubicación nueva del proveedor: ")
                except OperacionCancelada:
                    print("Operación cancelada; no se guardaron cambios.")
                    return False
            elif dato == "3":
                try:
                    nro = pedir_input("Ingrese el teléfono nuevo del proveedor: ")
                except OperacionCancelada:
                    print("Operación cancelada; no se guardaron cambios.")
                    return False
            else:
                print("La opción no existe")
                return False
        nombre_nuevo = self.nombre if nombre is None else str(nombre).strip()
        ubicacion_nueva = self.ubicacion if ubicacion is None else str(ubicacion).strip()
        nro_nuevo = self.nro if nro is None else nro
        if isinstance(nro_nuevo, str) and nro_nuevo.isdigit():
            nro_nuevo = int(nro_nuevo)
        if not nombre_nuevo:
            raise ValueError("El nombre no puede quedar vacío.")
        if not ubicacion_nueva:
            raise ValueError("La ubicación no puede quedar vacía.")
        if self.id is not None:
            from conexion import actualizar_proveedor
            actualizado = actualizar_proveedor(self.id, nombre_nuevo, nro_nuevo, ubicacion_nueva)
            if actualizado is None:
                return False
        if nombre is not None:
            if not str(nombre).strip():
                raise ValueError("El nombre no puede quedar vacío.")
            self.nombre = nombre_nuevo
        if ubicacion is not None:
            if not str(ubicacion).strip():
                raise ValueError("La ubicación no puede quedar vacía.")
            self.ubicacion = ubicacion_nueva
        if nro is not None:
            self.nro = nro_nuevo
        return True

    def agregar_producto(self):
        """Asocia un producto al proveedor en memoria; la persistencia se realiza desde el menú CRUD."""
        from main import OperacionCancelada, pedir_input
        try:
            cod = pedir_input("Ingrese el código del producto: ")
        except OperacionCancelada:
            print("Operación cancelada; no se guardaron cambios.")
            return None
        if any(str(producto.codigo) == cod for producto in self.productos):
            print("El producto ya existe")
            return None
        try:
            nombre = pedir_input("Ingrese el nombre: ")
            precio = pedir_input("Ingrese el precio: ")
            stock = pedir_input("Ingrese el stock: ")
            marca = pedir_input("Ingrese la marca: ")
            perecedero = pedir_input("¿Es perecedero? 1-Sí / 0-No: ")
        except OperacionCancelada:
            print("Operación cancelada; no se guardaron cambios.")
            return None
        if perecedero not in ("0", "1"):
            print("La opción debe ser 0 o 1.")
            return None
        producto = Producto(cod, nombre, precio, int(stock), marca, self, perecedero == "1")
        self.productos.append(producto)
        print("Producto agregado correctamente")
        return producto

    def consultar_productos(self):
        # CÓDIGO AGREGADO POR CODEX: refresca la relación con los datos persistidos.
        if self.id is not None:
            try:
                from conexion import productos_de_proveedor
                self.productos = productos_de_proveedor(self.id)
            except Exception as error:
                print(f"No se pudieron consultar los productos en MySQL: {error}")
        print(f"Productos de {self.nombre}:")
        for producto in self.productos:
            print(f"- {producto.nombre} (código {producto.codigo})")
        return self.productos


class Movimientos_Stock:
    # Se conserva la clase de POO de la etapa actual, sin persistencia de historial.
    # CÓDIGO AGREGADO POR CODEX: la persistencia ocurre en conexion.registrar_movimiento dentro de una transacción.
    def __init__(self, id, tipo, producto, cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que cero.")
        self.id = id
        self.tipo = tipo
        self.producto = producto
        self.cantidad = cantidad
        ahora = datetime.now()
        self.fecha = ahora.date()
        self.hora = ahora.time()
        self.fecha_hora = ahora

    def registrar_mov(self):
        print("Movimiento registrado")
        print("Producto:", self.producto.nombre)
        print("Tipo:", self.tipo)
        print("Cantidad:", self.cantidad)
        print("Fecha:", self.fecha)
        print("Hora:", self.hora)
        return self
