"""Category 모델."""

from extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "slug": self.slug}
