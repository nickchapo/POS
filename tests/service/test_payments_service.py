import uuid
from unittest.mock import Mock

import pytest

from app.infra.core.adapter.exchange_rate_target import ExchangeRateTarget
from app.infra.core.currency import Currency
from app.infra.core.domain.request.add_payment_request import AddPaymentRequest
from app.infra.core.errors import DoesNotExistError, ExistsError
from app.infra.core.repository.payments import PaymentRepository, Payment
from app.infra.core.service.payments import PaymentService
from app.infra.core.service.receipts import ReceiptService


@pytest.fixture
def payment_service():
    receipt_service = Mock(spec=ReceiptService)
    exchange_rate_target = Mock(spec=ExchangeRateTarget)
    payment_repository = Mock(spec=PaymentRepository)
    return PaymentService(receipt_service, exchange_rate_target, payment_repository)


def test_calculate_total_gel(payment_service):
    receipt_id = uuid.uuid4()
    products = [Mock(price=100.0), Mock(price=200.0)]
    total_gel = sum(product.price for product in products)

    payment_service.receipt_service.get_receipt.return_value = Mock(products=products)
    payment_service.payment_repository.receipt_has_payment.return_value = False

    response = payment_service.calculate_total(receipt_id, Currency.GEL)

    assert response.receipt_id == receipt_id
    assert response.amount == total_gel
    assert response.currency == Currency.GEL

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)


def test_calculate_total_foreign_currency(payment_service):
    receipt_id = uuid.uuid4()
    products = [Mock(price=100.0), Mock(price=200.0)]
    total_gel = sum(product.price for product in products)
    exchange_rate = 0.35
    converted_amount = round(total_gel * exchange_rate, 2)

    payment_service.receipt_service.get_receipt.return_value = Mock(products=products)
    payment_service.payment_repository.receipt_has_payment.return_value = False
    payment_service.exchange_rate_target.get_exchange_rate.return_value = exchange_rate

    response = payment_service.calculate_total(receipt_id, Currency.USD)

    assert response.receipt_id == receipt_id
    assert response.amount == converted_amount
    assert response.currency == Currency.USD

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)
    payment_service.exchange_rate_target.get_exchange_rate.assert_called_once_with(Currency.GEL, Currency.USD)


def test_calculate_total_no_products(payment_service):
    receipt_id = uuid.uuid4()
    payment_service.receipt_service.get_receipt.return_value = Mock(products=[])

    response = payment_service.calculate_total(receipt_id, Currency.GEL)

    assert response.receipt_id == receipt_id
    assert response.amount == 0.0
    assert response.currency == Currency.GEL

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)


def test_calculate_total_receipt_not_exist(payment_service):
    receipt_id = uuid.uuid4()
    payment_service.receipt_service.get_receipt.return_value = None

    with pytest.raises(DoesNotExistError):
        payment_service.calculate_total(receipt_id, Currency.GEL)

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)


def test_add_payment_to_receipt_success(payment_service):
    receipt_id = uuid.uuid4()
    dummy_receipt = Mock()
    dummy_receipt.products = []
    payment_service.receipt_service.get_receipt.return_value = dummy_receipt
    payment_service.payment_repository.receipt_has_payment.return_value = False

    request = AddPaymentRequest(currency=Currency.USD, amount=150.0)
    dummy_payment = Payment(
        receipt_id=receipt_id,
        amount=request.amount,
        currency=request.currency
    )
    payment_service.payment_repository.add.return_value = dummy_payment

    response = payment_service.add_payment_to_receipt(receipt_id, request)

    assert response.receipt_id == receipt_id
    assert response.amount == request.amount
    assert response.currency == request.currency

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)
    payment_service.payment_repository.receipt_has_payment.assert_called_once_with(receipt_id)
    payment_service.payment_repository.add.assert_called_once()


def test_add_payment_to_receipt_receipt_not_exist(payment_service):
    receipt_id = uuid.uuid4()
    payment_service.receipt_service.get_receipt.return_value = None

    request = AddPaymentRequest(currency=Currency.USD, amount=150.0)

    with pytest.raises(DoesNotExistError):
        payment_service.add_payment_to_receipt(receipt_id, request)

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)


def test_add_payment_to_receipt_already_exists(payment_service):
    receipt_id = uuid.uuid4()
    dummy_receipt = Mock()
    dummy_receipt.products = []
    payment_service.receipt_service.get_receipt.return_value = dummy_receipt
    payment_service.payment_repository.receipt_has_payment.return_value = True

    request = AddPaymentRequest(currency=Currency.USD, amount=150.0)

    with pytest.raises(ExistsError):
        payment_service.add_payment_to_receipt(receipt_id, request)

    payment_service.receipt_service.get_receipt.assert_called_once_with(receipt_id)
    payment_service.payment_repository.receipt_has_payment.assert_called_once_with(receipt_id)
