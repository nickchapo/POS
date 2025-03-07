import uuid

import pytest

from app.core.errors import DoesNotExistError, ExistsError
from app.core.repository.products import Product
from app.infra.sqlite.products import ProductSQLite


@pytest.fixture
def repo() -> ProductSQLite:
    repository = ProductSQLite(":memory:")
    repository.clear()
    return repository


def test_product_exists_true(repo: ProductSQLite) -> None:
    product_id = uuid.uuid4()
    product = Product(id=product_id, name="Test Product", barcode="123456", price=10.0)
    repo.add(product)
    assert repo.exists(product_id) is True


def test_product_exists_false(repo: ProductSQLite):
    non_existing_id = uuid.uuid4()
    assert repo.exists(non_existing_id) is False


def test_add_and_read_product(repo: ProductSQLite) -> None:
    product_id = uuid.uuid4()
    product = Product(id=product_id, name="Test Product", barcode="123456", price=10.0)
    repo.add(product)
    retrieved = repo.read(product_id)
    assert retrieved.id == product.id
    assert retrieved.name == product.name
    assert retrieved.barcode == product.barcode
    assert retrieved.price == product.price


def test_add_duplicate_name(repo: ProductSQLite) -> None:
    product1 = Product(id=uuid.uuid4(), name="prod", barcode="111", price=5.0)
    product2 = Product(id=uuid.uuid4(), name="prod", barcode="222", price=6.0)
    repo.add(product1)
    with pytest.raises(ExistsError) as excinfo:
        repo.add(product2)
    assert "name" in str(excinfo.value)


def test_add_duplicate_barcode(repo: ProductSQLite) -> None:
    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="dup", price=5.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="dup", price=6.0)
    repo.add(product1)
    with pytest.raises(ExistsError) as excinfo:
        repo.add(product2)
    assert "barcode" in str(excinfo.value)


def test_read_nonexistent_product(repo: ProductSQLite) -> None:
    non_existent_id = uuid.uuid4()
    with pytest.raises(DoesNotExistError):
        repo.read(non_existent_id)


def test_update_price(repo: ProductSQLite) -> None:
    product_id = uuid.uuid4()
    product = Product(id=product_id, name="Product", barcode="123", price=10.0)
    repo.add(product)
    new_price = 15.0
    repo.update_price(product_id, new_price)
    updated_product = repo.read(product_id)
    assert updated_product.price == new_price


def test_update_receipt_id(repo: ProductSQLite) -> None:
    product_id = uuid.uuid4()
    receipt_id = uuid.uuid4()
    product = Product(id=product_id, name="Product", barcode="123", price=10.0)
    repo.add(product)
    repo.update_receipt_id(product_id, receipt_id)


def test_list_and_clear_products(repo: ProductSQLite) -> None:
    product1 = Product(id=uuid.uuid4(), name="Product1", barcode="barcode1", price=10.0)
    product2 = Product(id=uuid.uuid4(), name="Product2", barcode="barcode2", price=20.0)
    repo.add(product1)
    repo.add(product2)
    products = repo.read_list()
    assert len(products) == 2
    repo.clear()
    products_after_clear = repo.read_list()
    assert len(products_after_clear) == 0
