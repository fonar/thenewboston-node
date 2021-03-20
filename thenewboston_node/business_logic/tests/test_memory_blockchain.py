import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.usefixtures('forced_memory_blockchain')
def test_can_forced_memory_blockchain():
    assert isinstance(BlockchainBase.get_instance(), MemoryBlockchain)


def test_get_initial_account_root_file(
    forced_memory_blockchain: MemoryBlockchain, initial_account_root_file, initial_account_root_file_dict
):
    initial_account_root_file_from_blockchain = forced_memory_blockchain.get_initial_account_root_file()
    assert initial_account_root_file_from_blockchain == initial_account_root_file
    assert initial_account_root_file_from_blockchain.to_dict() == initial_account_root_file_dict  # type: ignore


def test_get_account_balance_from_initial_account_root_file(
    forced_memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair,
    initial_account_root_file: AccountRootFile
):
    account = treasury_account_key_pair.public
    assert forced_memory_blockchain.get_account_balance(account) == 281474976710656
    assert forced_memory_blockchain.get_account_balance(account
                                                        ) == initial_account_root_file.get_balance_value(account)


@pytest.mark.skip('Not implemented yet')
@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_add_block(
    forced_memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair
):
    block = Block.from_main_transaction(
        user_account_key_pair.public, 31, signing_key=treasury_account_key_pair.private
    )
    forced_memory_blockchain.add_block(block)
    raise NotImplementedError
