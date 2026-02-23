from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, Date, ForeignKeyConstraint, Identity, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'User'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='User_pkey'),
        Index('User_email_key', 'email', postgresql_include=[], unique=True)
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'STAFF'::text"))
    position: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'STAFF'::text"))
    isActive: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updatedAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    lastLogin: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))


class Method(Base):
    __tablename__ = 'method'
    __table_args__ = (
        PrimaryKeyConstraint('id_method', name='method_pkey'),
    )

    id_method: Mapped[int] = mapped_column(Integer, primary_key=True)
    method: Mapped[Optional[str]] = mapped_column(String)

    transaction: Mapped[list['Transaction']] = relationship('Transaction', back_populates='method')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        PrimaryKeyConstraint('id_product', name='product_pkey'),
    )

    id_product: Mapped[int] = mapped_column(Integer, primary_key=True)
    product: Mapped[Optional[str]] = mapped_column(String)

    transaction: Mapped[list['Transaction']] = relationship('Transaction', back_populates='product')


class Retailer(Base):
    __tablename__ = 'retailer'
    __table_args__ = (
        PrimaryKeyConstraint('id_retailer', name='retailer_pkey'),
    )

    id_retailer: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    retailer_name: Mapped[Optional[str]] = mapped_column(String)

    transaction: Mapped[list['Transaction']] = relationship('Transaction', back_populates='retailer')


class State(Base):
    __tablename__ = 'state'
    __table_args__ = (
        PrimaryKeyConstraint('id_state', name='state_pkey'),
    )

    id_state: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    state: Mapped[Optional[str]] = mapped_column(String)

    city: Mapped[list['City']] = relationship('City', back_populates='state')


class UploadHistory(Base):
    __tablename__ = 'upload_history'
    __table_args__ = (
        PrimaryKeyConstraint('id_upload', name='upload_history_pkey'),
    )

    id_upload: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    system_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=6), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    total_rows: Mapped[Optional[int]] = mapped_column(Integer)


class City(Base):
    __tablename__ = 'city'
    __table_args__ = (
        ForeignKeyConstraint(['id_state'], ['state.id_state'], name='fk_city_state'),
        PrimaryKeyConstraint('id_city', name='city_pkey')
    )

    id_city: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_state: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String)

    state: Mapped['State'] = relationship('State', back_populates='city')
    transaction: Mapped[list['Transaction']] = relationship('Transaction', back_populates='city')


class Transaction(Base):
    __tablename__ = 'transaction'
    __table_args__ = (
        ForeignKeyConstraint(['id_city'], ['city.id_city'], name='fk_transaction_city1'),
        ForeignKeyConstraint(['id_method'], ['method.id_method'], name='fk_transaction_method1'),
        ForeignKeyConstraint(['id_product'], ['product.id_product'], name='fk_transaction_product1'),
        ForeignKeyConstraint(['id_retailer'], ['retailer.id_retailer'], name='fk_transaction_retailer1'),
        PrimaryKeyConstraint('id_transaction', 'id_retailer', 'id_product', 'id_method', 'id_city', name='transaction_pkey')
    )

    id_transaction: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    id_retailer: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_product: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_method: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_city: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    price_per_unit: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    unit_sold: Mapped[Optional[int]] = mapped_column(Integer)
    total_sales: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    operating_profit: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    operating_margin: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)

    city: Mapped['City'] = relationship('City', back_populates='transaction')
    method: Mapped['Method'] = relationship('Method', back_populates='transaction')
    product: Mapped['Product'] = relationship('Product', back_populates='transaction')
    retailer: Mapped['Retailer'] = relationship('Retailer', back_populates='transaction')
