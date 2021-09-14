import msgpack
from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.storages.file_system import read_compressed_file
from thenewboston_node.business_logic.tests.base import force_blockchain
from thenewboston_node.business_logic.utils.blockchain_state import read_block_chunk_file_from_source

from typing import cast
from more_itertools import ilen


API_V1_LIST_BLOCKCHAIN_STATE_URL = '/api/v1/block-chunks-meta/'


def read_block_chunk_file_from_source(source):
    data = read_compressed_file(source)

    unpacker = msgpack.Unpacker()
    unpacker.feed(cast(bytes, data))

    for block_compact_dict in unpacker:
        yield Block.from_compact_dict(block_compact_dict)


def test_yield_blocks_slice(api_client, file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks

    with force_blockchain(blockchain):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    data = response.json()

    url_path = data['results'][0]['url_path']
    file_path = url_path.replace(
        '/blockchain',
        blockchain.get_base_directory(),
    )

    data = read_block_chunk_file_from_source(file_path)
    assert ilen(data) == 3
