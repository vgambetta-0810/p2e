# ===== CÓDIGO ORIGINAL DEL GRUPO =====
# Se conservaron las clases, sus nombres principales, atributos y métodos
# iniciados por el grupo. Las correcciones y agregados están marcados debajo.
# ===== FIN CÓDIGO ORIGINAL DEL GRUPO =====

# ===== CORRECCIÓN DE CODEX =====
from datetime import datetime
# ===== FIN CORRECCIÓN DE CODEX =====


# ===== CÓDIGO AGREGADO POR CODEX =====
# Lista sencilla para detectar c?digos repetidos entre proveedores.
PRODUCTOS_REGISTRADOS = []
# ===== FIN CÓDIGO AGREGADO POR CODEX =====


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
    def __init__(self, codigo, nombre, precio: float, stock: int,
                 marca="No informada", proveedor=None, perecedero=False):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = float(precio)
        # CÓDIGO AGREGADO POR CODEX: el stock solo cambia con métodos validados.
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
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise ValueError("El stock inicial debe ser un entero no negativo")
        return stock

    @staticmethod
    def _validar_cantidad(cantidad):
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que cero")

    def aumentar_stock(self, cantidad):
        self._validar_cantidad(cantidad)
        self._stock += cantidad
        return self._stock

    def disminuir_stock(self, cantidad):
        self._validar_cantidad(cantidad)
        if cantidad > self._stock:
            print("ERROR: No existe stock suficiente.")
            return False
        self._stock -= cantidad
        return self._stock

    def actualizar_stock(self, stock):
        # Compatibilidad con el método anterior: permite únicamente aumentos o reducciones válidos.
        nuevo = self._validar_stock_inicial(stock)
        diferencia = nuevo - self._stock
        if diferencia > 0:
            self.aumentar_stock(diferencia)
        elif diferencia < 0:
            self.disminuir_stock(-diferencia)

    def esta_disponible(self):
        disponible = self.stock > 0
        print("El producto sí está disponible" if disponible
              else "El producto no está disponible")
        return disponible


class Proveedor:
    def __init__(self, id, nombre, ubicacion, nro):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.nro = nro
        self.productos = []

    def actualizar_datos(self):
        dato = input("Seleccione 1 para modificar nombre, 2 para modificar ubicación o 3 para modificar NRO telefónico: ")
        if dato == "1":
            self.nombre = input("Ingrese el nombre nuevo del proveedor: ")
        elif dato == "2":
            self.ubicacion = input("Ingrese la ubicación nueva del proveedor: ")
        elif dato == "3":
            self.nro = input("Ingrese el NRO telefónico nuevo del proveedor: ")
        else:
            print("La opción no existe")

    def agregar_producto(self):
        """Intenta crear un producto nuevo y lo asocia a este proveedor."""
        cod = input("Ingrese el código del producto: ")
        # ===== CORRECCIÓN DE CODEX =====
        for producto in PRODUCTOS_REGISTRADOS:
            if str(producto.codigo) == str(cod):
                print("El producto ya existe")
                return None
        # ===== FIN CORRECCIÓN DE CODEX =====

        nombre = input("Ingrese el nombre: ")
        precio = float(input("Ingrese el precio: "))
        stock = int(input("Ingrese el stock: "))
        marca = input("Ingrese la marca: ")
        perecedero = bool(int(input("¿Es perecedero? 1-Sí / 0-No: ")))
        producto = Producto(cod, nombre, precio, stock, marca, self, perecedero)

        # ===== CORRECCIÓN DE CODEX =====
        # El código original agregaba el mismo producto dos veces.
        self.productos.append(producto)
        PRODUCTOS_REGISTRADOS.append(producto)
        # ===== FIN CORRECCIÓN DE CODEX =====
        print("Producto agregado correctamente")
        return producto

    def consultar_productos(self):
        print(f"Productos de {self.nombre}:")
        for producto in self.productos:
            print(f"- {producto.nombre} (código {producto.codigo})")
        return self.productos


class Movimientos_Stock:
    def __init__(self, id, tipo, producto, cantidad):
        self.id = id
        self.tipo = tipo
        self.producto = producto
        self.cantidad = int(cantidad)
        # ===== CORRECCIÓN DE CODEX =====
        ahora = datetime.now()
        # ===== FIN CORRECCIÓN DE CODEX =====
        self.fecha = ahora.date()
        self.hora = ahora.time()

    def registrar_mov(self):
        print("Movimiento registrado")
        print("Producto:", self.producto.nombre)
        print("Tipo:", self.tipo)
        print("Cantidad:", self.cantidad)
        print("Fecha:", self.fecha)
        print("Hora:", self.hora)
        return self


# ===== CORRECCIÓN DE CODEX =====
class Administrador(Usuario):
    def gestionar_usuarios(self, usuarios):
        print(f"Usuarios registrados: {len(usuarios)}")
        return usuarios

    def gestionar_productos(self, productos):
        print(f"Productos registrados: {len(productos)}")
        return productos

    def gestionar_proveedores(self, proveedores):
        print(f"Proveedores registrados: {len(proveedores)}")
        return proveedores

    def consultar_movimientos(self, movimientos):
        for movimiento in movimientos:
            movimiento.registrar_mov()
        return movimientos


class Cajero(Usuario):
    def registrar_venta(self, producto, cantidad=1):
        cantidad = int(cantidad)
        if cantidad <= 0 or cantidad > producto.stock:
            print("No hay stock suficiente para realizar la venta")
            return False
        if producto.disminuir_stock(cantidad) is False:
            return False
        print(f"Venta registrada: {cantidad} unidad(es) de {producto.nombre}")
        return True

    def consultar_producto(self, producto):
        producto.mostrar_datos()
        return producto

    def consultar_stock(self, producto):
        return producto.consultar_stock()


class Cliente(Usuario):
    def consultar_producto(self, producto):
        producto.mostrar_datos()
        return producto

    def consultar_precio(self, producto):
        print(f"Precio de {producto.nombre}: ${producto.precio:.2f}")
        return producto.precio


# Se conservan los nombres que el grupo ya había utilizado.
admin = Administrador
cajero = Cajero
cliente = Cliente
# ===== FIN CORRECCIÓN DE CODEX =====


# ===== CÓDIGO AGREGADO POR CODEX =====
def demostrar_productos_desde_mysql():
    """Lee productos existentes y los convierte en objetos Producto."""
    # Reutiliza la conexi?n existente, configurada para PF2etapa en conexion.py.
    from conexion import conectar_mysql

    conexion = None
    cursor = None
    try:
        conexion = conectar_mysql()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id, nombre_producto, precio, stock, id_provedor FROM producto"
        )
        resultados = cursor.fetchall()
        productos_mysql = []
        for fila in resultados:
            # MySQL no tiene marca ni perecedero; se usan los valores por defecto.
            producto = Producto(
                fila[0], fila[1], fila[2], fila[3], proveedor=fila[4]
            )
            productos_mysql.append(producto)
            PRODUCTOS_REGISTRADOS.append(producto)
            producto.mostrar_datos()
        print(f"Productos le?dos desde MySQL: {len(productos_mysql)}")
        return productos_mysql
    except Exception as error:
        print(f"No se pudo consultar MySQL: {error}")
        return []
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()


def ejecutar_pruebas_locales():
    """Pruebas de POO que no modifican ninguna base de datos."""
    usuario = Usuario(123, "Ana", "Pérez", "111", "ana@mail.com")
    proveedor = Proveedor(1, "Proveedor de prueba", "Córdoba", "222")
    producto = Producto(10, "Producto de prueba", 100, 5,
                        "Marca de prueba", proveedor, False)
    proveedor.productos.append(producto)
    PRODUCTOS_REGISTRADOS.append(producto)
    proveedor.consultar_productos()
    producto.mostrar_datos()
    producto.consultar_stock()
    producto.esta_disponible()
    movimiento = Movimientos_Stock(1, "entrada", producto, 5)
    movimiento.registrar_mov()
    return usuario, proveedor, producto, movimiento


if __name__ == "__main__":
    # ===== PRUEBAS AGREGADAS POR CODEX =====
    ejecutar_pruebas_locales()
    demostrar_productos_desde_mysql()
    # ===== FIN PRUEBAS AGREGADAS POR CODEX =====
