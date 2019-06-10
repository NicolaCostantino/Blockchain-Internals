import hashlib
import json


def get_hash_of(block):
    """
    Creates a SHA-256 hash of a Block

    :param block: block
    """
    # The Dictionary must be ordered for avoiding inconsistent hashes
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def is_a_valid_chain(chain):
    if not len(chain) or len(chain) == 1:
        return True
    else:
        if chain[-1]['previous_hash'] == get_hash_of(chain[-2]):
            return is_a_valid_chain(chain[:-1])
        else:
            return False
