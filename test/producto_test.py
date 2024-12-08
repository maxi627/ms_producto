import os
import unittest

from app import create_app, db
from app.models import Producto


class ProductoTestCase(unittest.TestCase):
    
    def setUp(self):
        # User
        self.IDPRODUCTO_PRUEBA = 1
        self.FECHA_COMPRA_PRUEBA = '2020-01-01:00:00:00'
        self.DIRECCION_ENVIO_PRUEBA = "Calle falsa 123"
    
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def test_producto(self):
        producto = self.__get_producto()

        self.assertEqual(producto.producto_id, self.IDPRODUCTO_PRUEBA)
        self.assertEqual(producto.direccion_envio, self.DIRECCION_ENVIO_PRUEBA)
        self.assertEqual(producto.fecha_producto, self.FECHA_COMPRA_PRUEBA)

    def __get_producto(self):
        producto = Producto()
        producto.producto_id = self.IDPRODUCTO_PRUEBA
        producto.fecha_producto = self.FECHA_COMPRA_PRUEBA
        producto.direccion_envio = self.DIRECCION_ENVIO_PRUEBA

        return producto
    
if __name__ == '__main__':
    unittest.main()