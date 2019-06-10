import pytest
import random

from freezegun import freeze_time
from unittest import mock

from .blockchain import Blockchain as BlockchainSUT
from ..mark_1.tests import test_blockchain as parent


@pytest.fixture(scope="function")
def sample_sut():

    def _make_sample_sut(*args, **kwargs):
        return BlockchainSUT(*args, **kwargs)

    return _make_sample_sut


@pytest.fixture(scope="function")
def genesis_transaction():
    return {
        'unlock': '',
        'lock': ('output = The Times 03/Jan/2009 ' +
                 'Chancellor on brink of second bailout for banks'),
    }


@pytest.fixture(scope="function")
def initial_blockchain(sample_sut):

    def _make_initial_blockchain(sample_block_timestamp,
                                 genesis_block_data):
        with freeze_time(sample_block_timestamp):
            sut = sample_sut()
            sut._chain = []
            sut.current_transactions = [
                genesis_block_data,
            ]
            # Act
            retrieved_value = sut._create_genesis_block()
            return sut, retrieved_value

    return _make_initial_blockchain


@pytest.fixture(scope="function")
def sample_transaction_f():

    def _make_sample_transaction(unlock='', lock=''):
        return {
            'unlock': unlock if unlock else '',
            'lock': lock if lock else 'output=None',
        }

    return _make_sample_transaction


@pytest.fixture(scope="function")
def w_current_transactions_f(sample_transaction_f, sample_sut):

    def _make_with_transactions(number):
        sut = sample_sut()
        for iteration in range(number):  # pylint: disable=unused-variable
            sut.add_transaction(**sample_transaction_f())
        return sut

    return _make_with_transactions


class TestAddTransactionCreation(object):
    """
    Test the creation of a add transaction in a block
    """

    def test_on_empty_block_transactions_length(self,
                                                sample_sut,
                                                sample_transaction_f):
        # Arrange
        sut = sample_sut()
        # Act
        sample_transaction = sample_transaction_f()
        sut.add_transaction(**sample_transaction)
        # Assert
        assert len(sut.current_transactions) == 1

    def test_on_empty_block_transactions_value(self,
                                               sample_sut,
                                               sample_transaction_f):
        # Arrange
        sut = sample_sut()
        # Act
        sample_transaction = sample_transaction_f()
        sut.add_transaction(**sample_transaction)
        expected_transaction = {
            'input': sample_transaction['unlock'],
            'script': sample_transaction['lock'],
            'output': None,
        }
        # Assert
        assert sut.current_transactions[0] == expected_transaction

    def test_on_empty_block_custom_transactions_value(self,
                                                      sample_sut,
                                                      sample_transaction_f):
        # Arrange
        sut = sample_sut()
        # Act
        sample_transaction = sample_transaction_f(unlock='a = 1',
                                                  lock='output = a')
        sut.add_transaction(**sample_transaction)
        expected_transaction = {
            'input': sample_transaction['unlock'],
            'script': sample_transaction['lock'],
            'output': 1,
        }
        # Assert
        assert sut.current_transactions[0] == expected_transaction

    def test_on_not_empty_block_transactions_length(self,
                                                    w_current_transactions_f,
                                                    sample_transaction_f):
        # Arrange
        current_transaction_number = random.randint(1, 10)
        sut = w_current_transactions_f(current_transaction_number)
        prev_len = len(sut.current_transactions)
        # Act
        sample_transaction = sample_transaction_f()
        sut.add_transaction(**sample_transaction)
        # Assert
        assert len(sut.current_transactions) == prev_len + 1

    def test_on_not_empty_block_transactions_value(self,
                                                   w_current_transactions_f,
                                                   sample_transaction_f):
        # Arrange
        current_transaction_number = random.randint(1, 10)
        sut = w_current_transactions_f(current_transaction_number)
        # Act
        sample_transaction = sample_transaction_f()
        sut.add_transaction(**sample_transaction)
        expected_transaction = {
            'input': sample_transaction['unlock'],
            'script': sample_transaction['lock'],
            'output': None,
        }
        # Assert
        assert sut.current_transactions[-1] == expected_transaction


class TestCreateGenesisBlockMethod(object):
    """
    Test the create genesis block method
    """

    def test_add_transaction_called(self, sample_sut):
        # Arrange
        sut = sample_sut()
        sut._chain = []
        with mock.patch.object(sut, 'add_transaction'):
            # Act
            sut._create_genesis_block()
            # Assert
            sut.add_transaction.assert_called()  # pylint: disable=E1101

    def test_return_the_genesis_block(self,
                                      genesis_transaction,
                                      initial_blockchain):
        # Arrange
        sample_block_timestamp = '2009-01-03 18:15:05'
        genesis_block_data = genesis_transaction
        # Act
        sut, genesis_block = initial_blockchain(sample_block_timestamp,
                                                genesis_block_data)
        # Assert
        assert sut.genesis_block == genesis_block

    def test_return_None_if_already_started(self, sample_sut):
        # Arrange
        sut = sample_sut()
        # Act
        retrieved_value = sut._create_genesis_block()
        # Assert
        assert retrieved_value == None
