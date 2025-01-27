import pytest

from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.models import (
    Block, NodeDeclarationSignedChangeRequest, PrimaryValidatorScheduleSignedChangeRequest
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests.base import force_blockchain
from thenewboston_node.business_logic.tests.factories import add_blocks

API_V1_NODES_PREFIX = '/api/v1/nodes'


def test_node_not_found(file_blockchain, api_client):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_NODES_PREFIX + '/non_existing_id/')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Node not found'


def test_can_get_node(file_blockchain, api_client, user_account_key_pair):
    blockchain = file_blockchain

    nodes = list(blockchain.yield_nodes())
    assert len(nodes) == 1
    pv_node = nodes[0]

    node_declaration_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )
    block = Block.create_from_signed_change_request(
        blockchain,
        signed_change_request=node_declaration_request,
        pv_signing_key=user_account_key_pair.private,
    )
    blockchain.add_block(block)

    node = node_declaration_request.message.node

    with force_blockchain(blockchain):
        response = api_client.get(f'{API_V1_NODES_PREFIX}/{node.identifier}/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == node.identifier
    assert data['fee_amount'] == 3
    assert data['network_addresses'] == ['http://my.domain.com/']

    with force_blockchain(blockchain):
        response = api_client.get(f'{API_V1_NODES_PREFIX}/{pv_node.identifier}/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == pv_node.identifier
    assert data['fee_amount'] == pv_node.fee_amount
    assert pv_node.network_addresses
    assert data['network_addresses'] == pv_node.network_addresses


def test_can_get_self_node(file_blockchain, api_client):
    blockchain = file_blockchain

    nodes = list(blockchain.yield_nodes())
    assert len(nodes) == 1
    pv_node = nodes[0]

    with force_blockchain(blockchain):
        response = api_client.get(API_V1_NODES_PREFIX + '/self/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == pv_node.identifier
    assert data['fee_amount'] == pv_node.fee_amount
    assert pv_node.network_addresses
    assert data['network_addresses'] == pv_node.network_addresses


def test_can_get_primary_validator_node(file_blockchain, api_client):
    blockchain = file_blockchain

    nodes = list(blockchain.yield_nodes())
    assert len(nodes) == 1
    pv_node = nodes[0]

    with force_blockchain(blockchain):
        response = api_client.get(f'{API_V1_NODES_PREFIX}/pv/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == pv_node.identifier
    assert data['fee_amount'] == pv_node.fee_amount
    assert pv_node.network_addresses
    assert data['network_addresses'] == pv_node.network_addresses


@pytest.mark.parametrize(
    'blocks, node_role, add_pv', [
        (0, NodeRole.CONFIRMATION_VALIDATOR, False),
        (1, NodeRole.PRIMARY_VALIDATOR, False),
        (5, NodeRole.PRIMARY_VALIDATOR, False),
        (6, NodeRole.REGULAR_NODE, True),
    ]
)
def test_node_roles(
    file_blockchain, api_client, treasury_account_key_pair, blocks, node_role, user_account_key_pair, add_pv
):
    blockchain = file_blockchain
    add_blocks(blockchain, blocks, treasury_account_key_pair.private)

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(1, 5, get_node_signing_key())
    block = Block.create_from_signed_change_request(blockchain, pvs_request, get_node_signing_key())
    blockchain.add_block(block)

    if add_pv:
        nd_request = NodeDeclarationSignedChangeRequest.create(
            network_addresses=['http://localhost:8555/'], fee_amount=1, signing_key=user_account_key_pair.private
        )
        blockchain.add_block(Block.create_from_signed_change_request(blockchain, nd_request, get_node_signing_key()))
        pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(6, 10, user_account_key_pair.private)
        block = Block.create_from_signed_change_request(blockchain, pvs_request, get_node_signing_key())
        blockchain.add_block(block)

    with force_blockchain(blockchain):
        response = api_client.get(f'{API_V1_NODES_PREFIX}/self/')

    assert response.status_code == 200
    assert response.json()['role'] == node_role.value
