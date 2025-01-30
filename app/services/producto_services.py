

#TODO //LISTO: refactorizar
#TODO //LISTO: Justificar el cache y revisar o cambiar
#TODO //LISTO: Justificar el uso de redis
#TODO //LISTO: Justificar el uso de contextmanager
#TODO //LISTO: Justificar el uso de time


from app import cache, redis_client  # Se asume que `redis_client` es una instancia de Redis configurada
from app.models import Producto
from app.repositories import ProductoRepository
from contextlib import contextmanager
import time

class ProductoService:
    """
    Servicio para gestionar productos, incluyendo operaciones de caché, persistencia,
    manejo de actualizaciones y bloqueos en Redis para resolver problemas de concurrencia.
    """
    CACHE_TIMEOUT = 300  # Tiempo de expiración de caché en segundos
    REDIS_LOCK_TIMEOUT = 10  # Tiempo de bloqueo en Redis en segundos

    def __init__(self, repository=None):
        self.repository = repository or ProductoRepository()

    @contextmanager
    def redis_lock(self, producto_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis.
        :param producto_id: ID del producto que se bloqueará.
        """
        lock_key = f"producto_lock_{producto_id}"
        lock_value = str(time.time())

        # Intentar adquirir el bloqueo
        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield  # Permite la ejecución del bloque protegido
            finally:
                # Eliminar el bloqueo después de usarlo
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso está bloqueado para el producto {producto_id}.")

    def all(self) -> list[Producto]:
        """
        Obtiene la lista de todos los productos, con caché.
        :return: Lista de objetos Producto.
        """
        cached_productos = cache.get('productos')
        if cached_productos is None:
            productos = self.repository.get_all()
            if productos:
                cache.set('productos', productos, timeout=self.CACHE_TIMEOUT)
            return productos
        return cached_productos

    def add(self, producto: Producto) -> Producto:
        """
        Agrega un nuevo producto y actualiza la caché.
        :param producto: Objeto Producto a agregar.
        :return: Objeto Producto recién creado.
        """
        new_producto = self.repository.save(producto)
        cache.set(f'producto_{new_producto.id}', new_producto, timeout=self.CACHE_TIMEOUT)
        cache.delete('productos')  # Invalida la lista de productos en caché
        return new_producto

    def update(self, producto_id: int, updated_producto: Producto) -> Producto:
        """
        Actualiza un producto existente.
        :param producto_id: ID del producto a actualizar.
        :param updated_producto: Datos del producto actualizado.
        :return: Objeto Producto actualizado.
        """
        with self.redis_lock(producto_id):
            existing_producto = self.find(producto_id)
            if not existing_producto:
                raise Exception(f"Producto con ID {producto_id} no encontrado.")

            # Validación de los datos 
            if updated_producto.precio < 0:
                raise ValueError("El precio no puede ser negativo.")

            # Actualizar los datos del producto existente
            existing_producto.nombre = updated_producto.nombre
            existing_producto.precio = updated_producto.precio
            existing_producto.activado = updated_producto.activado
            
            saved_producto = self.repository.save(existing_producto)

            # Actualizar la caché
            cache.set(f'producto_{producto_id}', saved_producto, timeout=self.CACHE_TIMEOUT)
            cache.delete('productos')  # Invalida la lista de productos en caché

            return saved_producto

    def delete(self, producto_id: int) -> bool:
        """
        Elimina un producto por su ID y actualiza la caché.
        :param producto_id: ID del producto a eliminar.
        :return: True si el producto fue eliminado, False en caso contrario.
        """
        with self.redis_lock(producto_id):
            deleted = self.repository.delete(producto_id)
            if deleted:
                cache.delete(f'producto_{producto_id}')
                cache.delete('productos')  # Invalida la lista de productos en caché
            return deleted

    def find(self, producto_id: int) -> Producto:
        """
        Busca un producto por su ID, con caché.
        :param producto_id: ID del producto a buscar.
        :return: Objeto Producto si se encuentra, None en caso contrario.
        """
        cached_producto = cache.get(f'producto_{producto_id}')
        if cached_producto is None:
            producto = self.repository.get_by_id(producto_id)
            if producto:
                cache.set(f'producto_{producto_id}', producto, timeout=self.CACHE_TIMEOUT)
            return producto
        return cached_producto
