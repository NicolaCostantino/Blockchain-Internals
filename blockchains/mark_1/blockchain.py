from time import time

from . import validation


class Blockchain:
    def __init__(self):
        self._chain = []
        self.current_transactions = []
        self.genesis_previous_hash = '0'

        # Create the genesis block
        self.mine()

    @property
    def genesis_block(self):
        """
        Return the Genesis Block of the Blockchain
        """
        return self._chain[0] if len(self._chain) else None

    @property
    def last_block(self):
        """
        Return the last Block of the Blockchain
        """
        return self._chain[-1] if len(self._chain) else None

    def is_valid(self):
        """
        Determine the blockchain is valid

        :return: True if valid, False if not
        """
        return validation.is_a_valid_chain(self._chain)

    def get_chain(self):
        """
        Return the chain with the blocks in the right order

        :return: The chain
        """
        return self._chain

    def add_transaction(self, data):
        """
        Creates a new transaction to go into the next mined Block

        :param data: Data
        :return: The transaction
        """
        transaction = {
            'data': data,
        }
        self.current_transactions.append(transaction)
        return transaction

    def mine(self):
        """
        Execute the mining process that will create the next block

        :return: The created block
        """
        if not len(self._chain):
            return self._create_genesis_block()
        elif self.is_valid():
            return self._new_block()
        else:
            return None

    def _create_genesis_block(self):
        """
        Create the genesis block in the Blockchain if empty

        :return: New Block or None if Blockchain not empty
        """
        if not len(self._chain):
            previous_hash = self.genesis_previous_hash
            genesis_block_data = {
                'data': ('The Times 03/Jan/2009 ' +
                         'Chancellor on brink of second bailout for banks'),
            }
            # Create a genesis transaction
            self.add_transaction(**genesis_block_data)
            genesis_block = self._new_block(previous_hash=previous_hash)
            return genesis_block
        return None

    def _new_block(self, previous_hash=None):
        """
        Create a new Block in the Blockchain

        :param previous_hash: Hash of previous Block
        :return: New Block or None if no current transactions
        """

        if (len(self.current_transactions)):
            block = {
                'index': len(self._chain) + 1,
                'timestamp': time(),
                'transactions': self.current_transactions,
                'previous_hash': (previous_hash or
                                  self.get_hash_of(self.last_block)),
            }

            # Reset the current list of transactions
            self.current_transactions = []

            self._chain.append(block)
            return block
        return None

    def get_hash_of(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block: block
        """
        return validation.get_hash_of(block)
