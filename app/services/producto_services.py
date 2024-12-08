from app import cache
from app.models import Producto
from app.repositories import ProductoRepository

repository = ProductoRepository()

class ProductoService:
    def all(self) -> list[Producto]:
        result = cache.get('producto')
        if result is None:
            result = repository.get_all()
            if result:
                cache.set('producto', result, timeout=60)  # Considera un timeout más largo
        return result

    def add(self, producto: Producto) -> Producto:
        producto = repository.save(producto)
        cache.set(f'producto_{producto.id}', producto, timeout=60)
        cache.delete('producto')  # Invalida la lista de producto
        return producto

    def delete(self, id: int) -> bool:
        result = repository.delete(id)
        if result:
            cache.delete(f'producto_{id}')
            cache.delete('producto')  # Invalida la lista de producto
        return result

    def find(self, id: int) -> Producto:
        result = cache.get(f'producto_{id}')
        if result is None:
            result = repository.get_by_id(id)
            if result:
                cache.set(f'producto_{id}', result, timeout=60)
        return result
