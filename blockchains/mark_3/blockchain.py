from ..mark_1.blockchain import Blockchain as BlockchainMark1
from ..mark_1 import validation


class Blockchain(BlockchainMark1):
    def is_valid(self, chain=None):
        """
        Determine the blockchain is valid

        :return: True if valid, False if not
        """
        chain_to_validate = chain if chain else self._chain
        return validation.is_a_valid_chain(chain_to_validate)

    def evaluate_consensus(self, collected_chains):
        """
        The consensus algorithm.
        The internal chain is replaced with the received one if longer.

        :return: True if our chain was replaced, False if not
        """
        new_chain = None
        max_length = len(self.get_chain())

        for chain in collected_chains:
            length = len(chain)
            if length > max_length and self.is_valid(chain):
                # Found a new master blockchain
                max_length = length
                new_chain = chain

        if new_chain:
            self._chain = new_chain
            return True
        return False
