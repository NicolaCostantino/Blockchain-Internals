import pytest
import random
import time

from calendar import timegm
from freezegun import freeze_time
from unittest import mock

from ..blockchain import Blockchain as BlockchainSUT


# Fixtures

@pytest.fixture(scope="function")
def genesis_transaction():
    return {
        'data': ('The Times 03/Jan/2009 ' +
                 'Chancellor on brink of second bailout for banks'),
    }


@pytest.fixture(scope="function")
def sample_transaction_f():

    def _make_sample_transaction(sample=None):
        if not sample:
            token = list('The Times 03/Jan/2009 ' +
                         'Chancellor on brink of second bailout for banks')
            random.shuffle(token)
            token = ''.join(token)
        else:
            token = sample
        return {
            'data': token,
        }

    return _make_sample_transaction


@pytest.fixture(scope="function")
def sample_sut():

    def _make_sample_sut(*args, **kwargs):
        return BlockchainSUT(*args, **kwargs)

    return _make_sample_sut


@pytest.fixture(scope="function")
def initial_blockchain():

    def _make_initial_blockchain(sample_block_timestamp, genesis_block_data):
        with freeze_time(sample_block_timestamp):
            sut = BlockchainSUT()
            sut._chain = []
            sut.current_transactions = [
                genesis_block_data,
            ]
            # Act
            retrieved_value = sut._create_genesis_block()
            return sut, retrieved_value

    return _make_initial_blockchain


@pytest.fixture(scope="function")
def w_current_transactions_f(sample_transaction_f):

    def _make_with_transactions(number):
        sut = BlockchainSUT()
        for iteration in range(number):  # pylint: disable=unused-variable
            sut.add_transaction(**sample_transaction_f())
        return sut

    return _make_with_transactions


@pytest.fixture(scope="function")
def w_sample_blocks_f(sample_transaction_f, sample_sut):

    def _make_with_blocks(number,
                          min_transactions=1,
                          max_transactions=10):
        sut = sample_sut()
        for block in range(number):  # pylint: disable=unused-variable
            for transaction in range(random.randint(min_transactions,  # pylint: disable=unused-variable
                                                    max_transactions)):
                sut.add_transaction(**sample_transaction_f())
            sut.mine()
        return sut

    return _make_with_blocks


# Tests

class TestGenesisBlock(object):
    """
    Test that a blockchain starts with a genesis block
    """

    def test_init_calls_genesis_block_generation(self, sample_sut):
        # Arrange
        with mock.patch.object(BlockchainSUT, 'mine'):
            # Act
            sut = sample_sut()
            # Assert
            sut.mine.assert_called()  # pylint: disable=E1101

    def test_blockchain_has_only_one_block(self, sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        # Assert
        assert len(sut._chain) == 1

    def test_genesis_block_has_index_1(self, sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        # Assert
        assert sut.genesis_block['index'] == 1

    def test_genesis_block_timestamp(self, sample_sut):
        # Arrange
        genesis_block_timestamp = '2009-01-03 18:15:05'
        genesis_block_struct_time = time.strptime(
            '2009-01-03 18:15:05', '%Y-%m-%d %H:%M:%S')
        genesis_block_unix_timestamp = timegm(genesis_block_struct_time)
        # Act
        with freeze_time(genesis_block_timestamp):
            sut = sample_sut()
            # Assert
            assert (sut.genesis_block['timestamp'] ==
                    genesis_block_unix_timestamp)

    def test_genesis_block_has_the_sample_transaction(self, sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        # Assert
        assert len(sut.genesis_block['transactions']) == 1

    def test_genesis_block_sample_transaction_values(self,
                                                     genesis_transaction,
                                                     sample_sut):
        # Arrange
        sut = sample_sut()
        # Act
        retrieved_value = sut.genesis_block['transactions'][0]
        # Assert
        assert retrieved_value == genesis_transaction

    def test_genesis_block_has_previous_hash_0(self,sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        # Assert
        assert sut.genesis_block['previous_hash'] == '0'


class TestGenesisBlockProperty(object):
    """
    Test genesis block retrieving property
    """

    def test_returns_genesis_block_for_initial_blockchains(self,sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        # Assert
        assert sut.genesis_block == sut.last_block

    def test_returns_None_for_empty_blockchains(self,
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


class TestLastBlockProperty(object):
    """
    Test last block retrieving property
    """

    def test_returns_genesis_block_for_initial_blockchains(self, sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        # Assert
        assert sut.last_block == sut.genesis_block

    def test_returns_None_for_empty_blockchains(self, sample_sut):
        # Arrange
        # Act
        sut = sample_sut()
        sut._chain = []
        # Assert
        assert sut.last_block == None


class TestIsValidMethod(object):
    """
    Test the validation method of the blockchain
    """

    def test_on_empty_blockchain(self, sample_sut):
        # Arrange
        sut = sample_sut()
        sut._chain = []
        # Act
        retrieved_value = sut.is_valid()
        # Assert
        assert retrieved_value == True

    def test_on_genesis_block_only(self, sample_sut):
        # Arrange
        sut = sample_sut()
        # Act
        retrieved_value = sut.is_valid()
        # Assert
        assert retrieved_value == True

    def test_on_single_block_beyond_genesis_block(self,
                                                  sample_sut,
                                                  sample_transaction_f):
        # Arrange
        sut = sample_sut()
        transaction_data = sample_transaction_f()
        sut.add_transaction(**transaction_data)
        sut.mine()
        # Act
        retrieved_value = sut.is_valid()
        # Assert
        assert retrieved_value == True

    def test_on_manipulated_genesis_block(self, sample_sut):
        # Arrange
        sut = sample_sut()
        transaction_data = {
            'data': 'Satoshi Nakamoto',
        }
        sut.add_transaction(**transaction_data)
        sut.mine()
        sut.genesis_block['index'] = 23
        # Act
        retrieved_value = sut.is_valid()
        # Assert
        assert retrieved_value == False

    def test_on_some_blocks_beyond_genesis_block(self,
                                                 w_sample_blocks_f):
        # Arrange
        random_integer = random.randint(1, 10)
        sut = w_sample_blocks_f(random_integer)
        # Act
        retrieved_value = sut.is_valid()
        # Assert
        assert retrieved_value == True


class TestGetChainMethod(object):
    """
    Test the creation of a add transaction in a block
    """

    def test_returns_the_chain(self, sample_sut):
        # Arrange
        sut = sample_sut()
        # Act
        retrieved_value = sut.get_chain()
        # Assert
        assert retrieved_value == sut._chain


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
        # Assert
        assert sut.current_transactions[0] == sample_transaction

    def test_on_empty_block_custom_transactions_value(self,
                                                      sample_sut,
                                                      sample_transaction_f):
        # Arrange
        sut = sample_sut()
        # Act
        sample_transaction = sample_transaction_f(sample='Hello, World!')
        sut.add_transaction(**sample_transaction)
        # Assert
        assert sut.current_transactions[0] == sample_transaction

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
        # Assert
        assert sut.current_transactions[-1] == sample_transaction


class TestMineMethod(object):
    """
    Test the mine method
    """

    def test_on_empty_calls__create_genesis_block(self, sample_sut):
        # Arrange
        sut = sample_sut()
        sut._chain = []
        with mock.patch.object(sut, '_create_genesis_block'):
            # Act
            sut.mine()
            # Assert
            sut._create_genesis_block.assert_called()  # pylint: disable=E1101

    def test_on_empty_calls_is_valid(self, sample_sut):
        # Arrange
        sut = sample_sut()
        with mock.patch.object(sut, 'is_valid'):
            # Act
            sut.mine()
            # Assert
            sut.is_valid.assert_called()  # pylint: disable=E1101

    def test_on_empty_calls__new_block(self, sample_sut):
        # Arrange
        sut = sample_sut()
        with mock.patch.object(sut, '_new_block'):
            # Act
            sut.mine()
            # Assert
            sut._new_block.assert_called()  # pylint: disable=E1101

    def test_without_pending_transactions(self, sample_sut):
        # Arrange
        sut = sample_sut()
        # Act
        retrieved_value = sut.mine()
        # Assert
        assert retrieved_value == None

    def test_on_not_valid_chain(self, sample_sut):
        # Arrange
        sut = sample_sut()
        with mock.patch.object(sut, 'is_valid', return_value=False):
            # Act
            retrieved_value = sut.mine()
            # Assert
            assert retrieved_value == None


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
            sut._create_genesis_block()  # pylint: disable=E1101
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


class TestNewBlockMethod(object):
    """
    Test the creation of a new block in the blockchain
    """

    def test_no__new_block_with_empty_transactions(self, sample_sut):
        # Arrange
        sut = sample_sut()
        # Act
        retrieved_value = sut._new_block()
        # Assert
        assert retrieved_value == None

    def test_sample_block_generation(self,
                                     sample_sut,
                                     sample_transaction_f):
        # Arrange
        sut = sample_sut()
        current_transactions = [
            sample_transaction_f(),
            sample_transaction_f(),
        ]
        sut.current_transactions = current_transactions
        current_chain_length = len(sut._chain)
        # Act
        retrieved_value = sut._new_block()
        # Assert
        assert len(sut._chain) == current_chain_length + 1
        assert (len(retrieved_value['transactions']) ==
                len(current_transactions))
        assert (len(sut.last_block['transactions']) ==
                len(current_transactions))
        assert sut.last_block['transactions'] == current_transactions

    def test_previous_block_hash_assignment(self,
                                            sample_sut,
                                            sample_transaction_f):
        # Arrange
        sut = sample_sut()
        current_transactions = [
            sample_transaction_f(),
        ]
        previous_hash = sut.get_hash_of(sut.last_block)
        sut.current_transactions = current_transactions
        # Act
        retrieved_value = sut._new_block()
        # Assert
        assert retrieved_value['previous_hash'] == previous_hash

    def test_last_block_points_to_new_one(self,
                                          sample_sut,
                                          sample_transaction_f):
        # Arrange
        sut = sample_sut()
        current_transactions = [
            sample_transaction_f(),
        ]
        sut.current_transactions = current_transactions
        # Act
        retrieved_value = sut._new_block()
        # Assert
        assert sut.last_block == retrieved_value


class TestHashMethod(object):
    """
    Test the hash method of the Blockchain
    """

    @staticmethod
    def expected_hashing(block):
        import hashlib
        import json

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def test_on_genesis_block(self, sample_sut):
        # Arrange
        sut = sample_sut()
        expected_hash = self.expected_hashing(sut.last_block)
        # Act
        retrieved_hash = sut.get_hash_of(sut.last_block)
        # Assert
        assert expected_hash == retrieved_hash

    def test_on_generic_block(self,
                              sample_transaction_f,
                              w_sample_blocks_f):
        # Arrange
        random_integer = random.randint(1, 10)
        sut = w_sample_blocks_f(random_integer)
        previous_hash = sut.get_hash_of(sut.last_block)
        for transaction in range(random_integer):  # pylint: disable=unused-variable
            sut.add_transaction(sample_transaction_f())
        # Act
        retrieved_block = sut.mine()
        # Assert
        assert retrieved_block['previous_hash'] == previous_hash
