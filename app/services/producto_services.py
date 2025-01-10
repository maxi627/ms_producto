

#TODO //LISTO: refactorizar
#TODO //LISTO: Justificar el cache y revisar o cambiar
from app import cache
from app.models import Producto
from app.repositories import ProductoRepository

repository = ProductoRepository()

# ProductoService: Proporciona operaciones sobre productos con soporte para cacheo en Redis.
class ProductoService:
    CACHE_TIMEOUT = 300  # Timeout en segundos (300 segundos = 5 minutos)

    def all(self) -> list[Producto]:
        """
        Recupera todos los productos, utilizando caché para optimizar el rendimiento.
        """
        cache_key = f'{cache.config["CACHE_KEY_PREFIX"]}productos'
        result = cache.get(cache_key)
        if result is None:
            result = repository.get_all()
            if result:
                cache.set(cache_key, result, timeout=self.CACHE_TIMEOUT)
        return result

    def add(self, producto: Producto) -> Producto:
        """
        Agrega un nuevo producto, actualiza el caché correspondiente.
        """
        producto = repository.save(producto)
        self._invalidate_cache(producto.id)
        return producto

    def delete(self, id: int) -> bool:
        """
        Elimina un producto por ID y actualiza el caché correspondiente.
        """
        if repository.delete(id):
            self._invalidate_cache(id)
            return True
        return False

    def find(self, id: int) -> Producto:
        """
        Busca un producto por ID, utilizando caché para mejorar el rendimiento.
        """
        cache_key = f'{cache.config["CACHE_KEY_PREFIX"]}producto_{id}'
        result = cache.get(cache_key)
        if result is None:
            result = repository.get_by_id(id)
            if result:
                cache.set(cache_key, result, timeout=self.CACHE_TIMEOUT)
        return result

    def _invalidate_cache(self, producto_id: int) -> None:
        """
        Invalida el caché relacionado con el producto especificado y la lista de productos.
        """
        cache.delete(f'{cache.config["CACHE_KEY_PREFIX"]}producto_{producto_id}')
        cache.delete(f'{cache.config["CACHE_KEY_PREFIX"]}productos')
