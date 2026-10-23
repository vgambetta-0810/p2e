# CÓDIGO AGREGADO POR CODEX
"""Acceso a PF2etapa. Solo contiene consultas parametrizadas y transacciones."""
import os
from contextlib import contextmanager

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:  # Permite abrir el menú y usar las clases sin el conector.
    mysql = None
    Error = Exception


def conectar_mysql():
    if mysql is None:
        raise RuntimeError("Falta mysql-connector-python. Instalalo con: python -m pip install mysql-connector-python")
    configuracion = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "PF2etapa"),
        "connection_timeout": 5,
    }
    if not configuracion["password"]:
        raise RuntimeError("Configurá MYSQL_PASSWORD en las variables de entorno.")
    return mysql.connector.connect(**configuracion)


@contextmanager
def cursor_db(diccionario=False):
    conexion = conectar_mysql()
    cursor = conexion.cursor(dictionary=diccionario)
    try:
        yield conexion, cursor
    finally:
        cursor.close()
        conexion.close()


def verificar_esquema(cursor):
    """Valida las columnas conocidas antes de ejecutar operaciones CRUD."""
    esperado = {
        "producto": {"id", "nombre_producto", "precio", "stock", "id_provedor"},
        "provedor": {"id", "nombre_empresa", "cel", "ubicacion"},
    }
    for tabla, requeridas in esperado.items():
        cursor.execute(f"DESCRIBE `{tabla}`")
        existentes = {fila[0] for fila in cursor.fetchall()}
        if not requeridas.issubset(existentes):
            faltan = ", ".join(sorted(requeridas - existentes))
            raise RuntimeError(f"Esquema inesperado en {tabla}; faltan columnas: {faltan}")


def _producto(fila):
    from poo import Producto, Proveedor
    proveedor = Proveedor(fila["id_provedor"], fila.get("nombre_empresa") or "", fila.get("ubicacion") or "", fila.get("cel") or "")
    return Producto(fila["id"], fila["nombre_producto"], fila["precio"], fila["stock"], proveedor=proveedor)


def _proveedor(fila):
    from poo import Proveedor
    return Proveedor(fila["id"], fila["nombre_empresa"], fila["ubicacion"], fila["cel"])


def listar_productos():
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT p.id,p.nombre_producto,p.precio,p.stock,p.id_provedor,v.nombre_empresa,v.ubicacion,v.cel FROM producto p LEFT JOIN provedor v ON p.id_provedor=v.id ORDER BY p.id")
        return [_producto(x) for x in cur.fetchall()]


def buscar_producto(id_producto):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT p.id,p.nombre_producto,p.precio,p.stock,p.id_provedor,v.nombre_empresa,v.ubicacion,v.cel FROM producto p LEFT JOIN provedor v ON p.id_provedor=v.id WHERE p.id=%s", (id_producto,))
        fila = cur.fetchone()
        return _producto(fila) if fila else None


def productos_de_proveedor(id_proveedor):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT p.id,p.nombre_producto,p.precio,p.stock,p.id_provedor,v.nombre_empresa,v.ubicacion,v.cel FROM producto p JOIN provedor v ON p.id_provedor=v.id WHERE v.id=%s ORDER BY p.id", (id_proveedor,))
        return [_producto(x) for x in cur.fetchall()]


def proveedor_de_producto(id_producto):
    producto = buscar_producto(id_producto)
    return producto.proveedor if producto else None


def listar_proveedores():
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT id,nombre_empresa,cel,ubicacion FROM provedor ORDER BY id")
        return [_proveedor(x) for x in cur.fetchall()]


def buscar_proveedor(id_proveedor):
    with cursor_db(True) as (_, cur):
        verificar_esquema(cur)
        cur.execute("SELECT id,nombre_empresa,cel,ubicacion FROM provedor WHERE id=%s", (id_proveedor,))
        fila = cur.fetchone()
        return _proveedor(fila) if fila else None


def _guardar(sql, parametros):
    with cursor_db() as (conexion, cur):
        verificar_esquema(cur)
        cur.execute(sql, parametros)
        conexion.commit()
        return cur.lastrowid, cur.rowcount


def crear_producto(nombre, precio, stock, id_proveedor):
    if buscar_proveedor(id_proveedor) is None:
        raise ValueError("El proveedor indicado no existe.")
    nuevo_id, _ = _guardar("INSERT INTO producto (nombre_producto,precio,stock,id_provedor) VALUES (%s,%s,%s,%s)", (nombre, precio, stock, id_proveedor))
    return buscar_producto(nuevo_id)


def actualizar_producto(id_producto, nombre, precio, id_proveedor):
    if buscar_producto(id_producto) is None:
        return None
    if buscar_proveedor(id_proveedor) is None:
        raise ValueError("El proveedor indicado no existe.")
    _guardar("UPDATE producto SET nombre_producto=%s,precio=%s,id_provedor=%s WHERE id=%s", (nombre, precio, id_proveedor, id_producto))
    return buscar_producto(id_producto)


def eliminar_producto(id_producto):
    _, cuenta = _guardar("DELETE FROM producto WHERE id=%s", (id_producto,))
    return cuenta > 0


def cambiar_stock(id_producto, cantidad, aumentar):
    # La operación atómica evita sobrescribir un cambio concurrente y rechaza stock insuficiente.
    with cursor_db(True) as (conexion, cur):
        verificar_esquema(cur)
        cur.execute("SELECT id,nombre_producto,precio,stock,id_provedor FROM producto WHERE id=%s FOR UPDATE", (id_producto,))
        fila = cur.fetchone()
        if not fila:
            return None
        from poo import Producto
        producto = Producto(fila["id"], fila["nombre_producto"], fila["precio"], fila["stock"], proveedor=fila["id_provedor"])
        (producto.aumentar_stock if aumentar else producto.disminuir_stock)(cantidad)
        cur.execute("UPDATE producto SET stock=%s WHERE id=%s", (producto.consultar_stock(), id_producto))
        conexion.commit()
        return producto


def crear_proveedor(nombre, cel, ubicacion):
    nuevo_id, _ = _guardar("INSERT INTO provedor (nombre_empresa,cel,ubicacion) VALUES (%s,%s,%s)", (nombre, cel, ubicacion))
    return buscar_proveedor(nuevo_id)


def actualizar_proveedor(id_proveedor, nombre, cel, ubicacion):
    if buscar_proveedor(id_proveedor) is None:
        return None
    _guardar("UPDATE provedor SET nombre_empresa=%s,cel=%s,ubicacion=%s WHERE id=%s", (nombre, cel, ubicacion, id_proveedor))
    return buscar_proveedor(id_proveedor)


def eliminar_proveedor(id_proveedor):
    with cursor_db(True) as (conexion, cur):
        verificar_esquema(cur)
        cur.execute("SELECT COUNT(*) AS cantidad FROM producto WHERE id_provedor=%s", (id_proveedor,))
        if cur.fetchone()["cantidad"]:
            raise ValueError("El proveedor tiene productos asociados; resolvé esa relación antes de eliminarlo.")
        cur.execute("DELETE FROM provedor WHERE id=%s", (id_proveedor,))
        conexion.commit()
        return cur.rowcount > 0
