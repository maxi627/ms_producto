import os
import unittest
from redis import Redis
from app import create_app, cache, db
from app.models import Producto
from app.services import ProductoService

service = ProductoService()

class RedisTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['FLASK_ENV'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()

        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # test connection to Redis
    def test_redis_connection(self):
        redis = Redis(
            host=self.app.config['CACHE_REDIS_HOST'],
            port=self.app.config['CACHE_REDIS_PORT'],
            db=self.app.config['CACHE_REDIS_DB'],
            password=self.app.config['CACHE_REDIS_PASSWORD']
        )
        self.assertTrue(redis.ping())

    def test_cache_after_adding_producto(self):
        producto = Producto(nombre='Teclado mecanico', precio=45000.0, activado=True)
        producto1 = service.add(producto)

        cached_producto = cache.get(f'producto_{producto1.id}')

        self.assertIsNotNone(cached_producto)
        self.assertEqual(cached_producto.id, producto1.id)
        self.assertEqual(cached_producto.nombre, producto1.nombre)
        self.assertEqual(cached_producto.precio, producto1.precio)
        self.assertEqual(cached_producto.activado, producto1.activado)

if __name__ == '__main__':
    unittest.main()
