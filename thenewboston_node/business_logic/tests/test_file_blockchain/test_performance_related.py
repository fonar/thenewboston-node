from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain, get_start_end
from thenewboston_node.business_logic.tests.factories.block import make_block


def test_iter_blocks_from_cache(blockchain_directory):
    blockchain = FileBlockchain(blockchain_directory, validate=False)
    blockchain.blocks_cache[0] = block0 = make_block(message_hash='0')
    blockchain.blocks_cache[1] = block1 = make_block(message_hash='1')
    blockchain.blocks_cache[2] = block2 = make_block(message_hash='2')
    blockchain.blocks_cache[3] = block3 = make_block(message_hash='3')
    assert block0

    assert list(blockchain._iter_blocks_from_cache(1, 10, 1)) == [block1, block2, block3]
    assert list(blockchain._iter_blocks_from_cache(1, 2, 1)) == [block1, block2]
    assert list(blockchain._iter_blocks_from_cache(0, 3, -1)) == [block3, block2, block1, block0]
    assert list(blockchain._iter_blocks_from_cache(1, 2, -1)) == [block2, block1]


def test_get_start_end():
    assert get_start_end('00012-000101-block-chunk.msgpack') == (12, 101)
