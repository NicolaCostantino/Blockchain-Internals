from ..mark_1.blockchain import Blockchain as BlockchainMark1


class Blockchain(BlockchainMark1):

    def add_transaction(self, unlock, lock):
        """
        Creates a new transaction to go into the next mined Block

        :param script: script
        :return: The transaction
        """
        vm_globals = {}
        vm_locals = {}
        self._script_runner(unlock, vm_globals, vm_locals)
        self._script_runner(lock, vm_globals, vm_locals)
        transaction = {
            'input': unlock,
            'script': lock,
            'output': vm_locals.get('output', None),
        }
        self.current_transactions.append(transaction)
        return transaction

    def _create_genesis_block(self):
        """
        Create the genesis block in the Blockchain if empty

        :return: New Block or None if Blockchain not empty
        """
        if not len(self._chain):
            previous_hash = self.genesis_previous_hash
            genesis_block_data = {
                'unlock': '',
                'lock': ('output = The Times 03/Jan/2009 ' +
                          'Chancellor on brink of second bailout for banks'),
            }
            # Create a genesis transaction
            self.add_transaction(**genesis_block_data)
            genesis_block = self._new_block(previous_hash=previous_hash)
            return genesis_block
        return None

    def _script_runner(self, vm_script, vm_globals, vm_locals):
        try:
            exec(vm_script, vm_globals, vm_locals)
        except Exception as e:
            pass
        return
