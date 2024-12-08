from typing import List

from app import db
from app.models import Producto

from .repository import Repository_delete, Repository_get, Repository_save


class ProductoRepository(Repository_save, Repository_get, Repository_delete):
    def save(self, entity: Producto) -> Producto:
        db.session.add(entity)
        db.session.commit()
        return entity

    def get_all(self) -> List[Producto]:
        return Producto.query.all()

    def get_by_id(self, id: int) -> Producto:
        return Producto.query.get(id)

    def delete(self, id: int) -> bool:
        Producto = self.get_by_id(id)
        if Producto:
            db.session.delete(Producto)
            db.session.commit()
            return True
        return False
