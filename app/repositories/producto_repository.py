from typing import List

from app import db
from app.models import Producto

from .repository import Repository_delete, Repository_get, Repository_save


class ProductoRepository(Repository_save, Repository_get, Repository_delete):
    def save(self, entity: Producto) -> Producto:
        try:
            db.session.add(entity)  
            db.session.commit()  # Confirma la transacción
            return entity
        except Exception as e:
            db.session.rollback()  # Deshace la transacción si hay un error
            raise e  # Propaga la excepción para manejo externo

    def get_all(self) -> List[Producto]:
        return Producto.query.all()

    def get_by_id(self, id: int) -> Producto:
        return Producto.query.get(id)

    def delete(self, id: int) -> bool:
        try:
            producto = self.get_by_id(id)
            if producto:
                db.session.delete(producto)  
                db.session.commit()  
                return True
            return False
        except Exception as e:
            db.session.rollback()  # Deshace la transacción si hay un error
            raise e  # Propaga la excepción para manejo externo
