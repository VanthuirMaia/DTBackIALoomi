from sqlalchemy import Column, Integer, String, Text

from app.db.base import Base

# Modelo ORM da entidade Tinta

class Paint(Base):
    __tablename__ = "paints"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cor = Column(String(100), nullable=False)
    tipo_superficie = Column(String(100))
    ambiente = Column(String(100))
    acabamento = Column(String(100))
    features = Column(Text)
    linha = Column(String(100))

    def __repr__(self):
        return f"<Paint(id={self.id}, nome='{self.nome}', cor='{self.cor}')>"
