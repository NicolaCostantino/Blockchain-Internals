import pytest
import random

from ..blockchain import Blockchain as BlockchainSUT
from ...mark_1.tests import test_blockchain as TestMark1
from ...mark_1.tests.test_blockchain import (sample_transaction_f,
                                             w_sample_blocks_f)


@pytest.fixture(scope="function")
def sample_sut():

    def _make_sample_sut(*args, **kwargs):
        return BlockchainSUT(*args, **kwargs)

    return _make_sample_sut


class TestIsValidMethod(TestMark1.TestIsValidMethod):
    pass


class TestEvaluateConsensus(object):
    """
    Test the consensus algorithm
    """

    def test_on_empty_chains(self,
                             sample_sut):
        # Arrange
        sut = sample_sut()
        collected_chains = []
        # Act
        retrieved_value = sut.evaluate_consensus(collected_chains)
        # Assert
        assert retrieved_value == False

    def test_on_shorter_chain(self,
                              sample_sut,
                              w_sample_blocks_f):
        # Arrange
        sut = sample_sut()
        random_integer = random.randint(1, 10)
        longer_chain = w_sample_blocks_f(random_integer)
        # Act
        retrieved_value = sut.evaluate_consensus([longer_chain.get_chain()])
        # Assert
        assert retrieved_value == True

    def test_on_longerer_chain(self,
                               sample_sut,
                               w_sample_blocks_f):
        # Arrange
        random_integer = random.randint(1, 10)
        sut = w_sample_blocks_f(random_integer)
        shorter_chain = sample_sut()
        # Act
        retrieved_value = sut.evaluate_consensus([shorter_chain.get_chain()])
        # Assert
        assert retrieved_value == False
