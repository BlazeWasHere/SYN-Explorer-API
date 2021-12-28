#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import Dict

from hexbytes import HexBytes
from web3 import Web3
import pytest

from tests.helper import eth_get_log, avalanche_bridge_cb, polygon_bridge_cb, \
    bsc_get_log, arb_bridge_cb, eth_bridge_cb, avalanche_bridge_cb, \
    polygon_get_log, bsc_get_log, arb_get_log, avalanche_get_log, ftm_get_log, \
    bsc_bridge_cb, ftm_bridge_cb, movr_get_log, movr_bridge_cb
from explorer.utils.database import Transaction, LostTransaction
from explorer.utils.data import SYN_DATA


@pytest.fixture
def rpcs() -> Dict[str, Web3]:
    return {k: Web3(Web3.HTTPProvider(v['rpc'])) for k, v in SYN_DATA.items()}


def test_polygon_usdc_out(rpcs: Dict[str, Web3]) -> None:
    log = polygon_get_log(
        rpcs['polygon'],
        '0x505cb620a31c9bb1893f74b5d405c652e3a302115262b4c5e6e439860319b4cf',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0x081c9187ad515a873102bf3575fc72b8faf46b2905c4c17ba76bff72503aa6d0'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0xaaaa701efea3ac6b184628ed104f827014641592'),
        to_address=HexBytes('0xaaaa701efea3ac6b184628ed104f827014641592'),
        sent_value=20000000,
        received_value=None,
        pending=True,
        from_chain_id=137,
        to_chain_id=250,
        sent_time=1640682515,
        received_time=None,
        sent_token=HexBytes('0x2791bca1f2de4661ed88a30c99a7a9449aa84174'),
        received_token=HexBytes('0x04068da6c83afcfa0e13ba15a6696662335d5b75'),
        swap_success=None,
    )

    ret = polygon_bridge_cb(log)
    assert ret == expected


def test_polygon_gohm_in(rpcs: Dict[str, Web3]) -> None:
    log = polygon_get_log(
        rpcs['polygon'],
        '0x4339c55c81b5757de2172d69fc86bde11edce5b6eb2f6531b535f0329da3d415',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x2ab145d65c341d65e3628f542eb364d5197845b6d1e0b71c7aa44cad61aea6e1'
        ),
        to_address=HexBytes('0xc89048d9e96f16b3e4a5e9f84caea67517bdb411'),
        received_value=120131612094266528,
        to_chain_id=137,
        received_time=1640533438,
        received_token=HexBytes('0xd8ca34fd379d9ca3c6ee3b3905678320f5b45195'),
        swap_success=None,
        fee=60095853974120,
    )

    ret = polygon_bridge_cb(log)
    assert ret == expected


def test_eth_weth_in(rpcs: Dict[str, Web3]) -> None:
    log = eth_get_log(
        rpcs['ethereum'],
        '0x9cd9089fc3baec0376c57d07c2553920c3f7f6e2e9c9a4c472911de098e30f6f',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x3c6cd6479992285ccfcd454780871bda4a1ee778389fd71651f78e6b90400902'
        ),
        to_address=HexBytes('0x734c30744f7204d06ea09c9b3fc94553f755e8d7'),
        received_value=21886461743816518221,
        to_chain_id=1,
        received_time=1640536118,
        received_token=HexBytes('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
        swap_success=None,
        fee=30684004047008938,
    )

    ret = eth_bridge_cb(log)
    assert ret == expected


def test_avalanche_gohm_in(rpcs: Dict[str, Web3]) -> None:
    log = avalanche_get_log(
        rpcs['avalanche'],
        '0xc169e57d40a719e660e0b2530378e2cbee34a423515030e9af81fdb0aba9b348',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x275cac28b010c8f5913dfd2351aabc2cb51de5e6ef6f41d8d51ed42643b9ced3'
        ),
        to_address=HexBytes('0x872597b2c3ca35a189ec7691a45f831b77ee0c33'),
        received_value=249500000000000000,
        to_chain_id=43114,
        received_time=1640463136,
        received_token=HexBytes('0x321e7092a180bb43555132ec53aaa65a5bf84251'),
        swap_success=None,
        fee=500000000000000,
    )

    ret = avalanche_bridge_cb(log)
    assert ret == expected


def test_movr_synfrax_in(rpcs: Dict[str, Web3]) -> None:
    log = movr_get_log(
        rpcs['moonriver'],
        '0xb2090e2b8fb68a1ac2cce2ee4efc206faaeade44dd501f85d938013cbf05234b',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x78e4a8fc0feb8f1f34a8dac3e0fb456b13b71cc102aaf85c1db8fad1c3965d85'
        ),
        to_address=HexBytes('0x38fadaf9c2ae72b59720972c24ac9493fb43bb62'),
        received_value=4997000400000000000000,
        to_chain_id=1285,
        received_time=1640385180,
        received_token=HexBytes('0x1a93b23281cc1cde4c4741353f3064709a16197d'),
        swap_success=None,
        fee=1000000000000000000,
    )

    ret = movr_bridge_cb(log)
    assert ret == expected


def test_polygon_nusd_in_swap_fail(rpcs: Dict[str, Web3]) -> None:
    log = polygon_get_log(
        rpcs['polygon'],
        '0x875c4adb374491c8ae2af25c757c0383e1e88242d2cbb41eeaa03aeca915993d',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x79bef280920548e955f36690b5735d83d0ec39fafefd0555acdf0c1f0484c515'
        ),
        to_address=HexBytes('0xf0e4d0d6094d6e13f61013a663b56154546b6c4a'),
        received_value=199655687518112362792440,
        to_chain_id=137,
        received_time=1636284211,
        received_token=HexBytes('0xb6c473756050de474286bed418b77aeac39b02af'),
        swap_success=False,
        fee=79894232700325075147,
    )

    ret = polygon_bridge_cb(log)
    assert ret == expected


def test_ftm_nusd_in_swap_fail(rpcs: Dict[str, Web3]) -> None:
    log = ftm_get_log(
        rpcs['fantom'],
        '0x0000c68300000b1bd358f64dadfc79ac6c34ad8912161b628cbf06be1138011f',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0xfbc87b55553fefecb20fbf645f6885b42f4ed19bd3e8c8c488d1ed4926ae6363'
        ),
        to_address=HexBytes('0x70e09792e94b04cdb76abf7aa24781dcb4d37e2e'),
        received_value=11809477873423405296712,
        to_chain_id=250,
        received_time=1636283005,
        received_token=HexBytes('0xed2a7edd7413021d440b09d654f3b87712abab66'),
        swap_success=False,
        fee=4725681421938137373,
    )

    ret = ftm_bridge_cb(log)
    assert ret == expected


def test_eth_frax_in(rpcs: Dict[str, Web3]) -> None:
    log = eth_get_log(
        rpcs['ethereum'],
        '0xb3e9600e61dfbdfce360fcb10ee680bffade9c0bb8ad5441b1f04817fced605e',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x6cf618c56debbcae8425329d18b097da556bedb7d978d001760355cb0e15d0a9'
        ),
        to_address=HexBytes('0xce91783d36925bcc121d0c63376a248a2851982a'),
        received_value=39614107999999999475922,
        to_chain_id=1,
        received_time=1640452902,
        received_token=HexBytes('0x853d955acef822db058eb8505911ed77f175b99e'),
        swap_success=None,
        fee=100000000000000000000,
    )

    ret = eth_bridge_cb(log)
    assert ret == expected


def test_avalanche_weth_out(rpcs: Dict[str, Web3]) -> None:
    log = avalanche_get_log(
        rpcs['avalanche'],
        '0xb7c1219e58977f0448e1058378edaab3c6a875968a9d955210ff4627ec8ff778',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0xc55f8d6059337661e1540ae12fe57ed3d28b419443b3173a29e2abac6ae26606'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0xc6d725b42ddd3257f8ef05f807ac3155ac70af87'),
        to_address=HexBytes('0xc6d725b42ddd3257f8ef05f807ac3155ac70af87'),
        sent_value=121934824070437538,
        received_value=None,
        pending=True,
        from_chain_id=43114,
        to_chain_id=1,
        sent_time=1640448305,
        received_time=None,
        sent_token=HexBytes('0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab'),
        received_token=HexBytes('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
        swap_success=None,
    )

    ret = avalanche_bridge_cb(log)
    assert ret == expected


def test_polygon_nusd_out(rpcs: Dict[str, Web3]) -> None:
    log = polygon_get_log(
        rpcs['polygon'],
        '0xecbbb9514b5bc666e1c29651edf22fd625c0171176a6d1b1dbe03cdd14d1ec5c',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0x87e1ab6765ac2d86ecfe42687864d53b37d25591e7ee4294ac257f3859b1adce'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0x5c861c46131a6b5e8bbe62ac0758babc0102965b'),
        to_address=HexBytes('0x5c861c46131a6b5e8bbe62ac0758babc0102965b'),
        sent_value=5243089701582953600818,
        received_value=None,
        pending=True,
        from_chain_id=137,
        to_chain_id=1,
        sent_time=1640432933,
        received_time=None,
        sent_token=HexBytes('0x8f3cf7ad23cd3cadbd9735aff958023239c6a063'),
        received_token=HexBytes('0x6b175474e89094c44da98b954eedeac495271d0f'),
        swap_success=None,
    )

    ret = polygon_bridge_cb(log)
    assert ret == expected


def test_bsc_nusd_out(rpcs: Dict[str, Web3]) -> None:
    log = bsc_get_log(
        rpcs['bsc'],
        '0xfc1af288bb85d03a86552b4013ff632d472cbebe2b518445c312a0fc7d09dbd5',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0x8b88eb14f738fe1709ff6f1d79f081814ac8946e76d52b1a7971f87860804568'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0x38e799361128eaea9378cd39ac73c297fc9242f5'),
        to_address=HexBytes('0x38e799361128eaea9378cd39ac73c297fc9242f5'),
        sent_value=785000000000000000000,
        received_value=None,
        pending=True,
        from_chain_id=56,
        to_chain_id=137,
        sent_time=1640365015,
        received_time=None,
        sent_token=HexBytes('0x55d398326f99059ff775485246999027b3197955'),
        received_token=HexBytes('0xc2132d05d31c914a87c6611c10748aeb04b58e8f'),
        swap_success=None,
    )

    ret = bsc_bridge_cb(log)
    assert ret == expected


def test_arb_nusd_in(rpcs: Dict[str, Web3]) -> None:
    log = arb_get_log(
        rpcs['arbitrum'],
        '0xb3117378dc651d07d5dcbf00d97b52477c82cfb8c92bcaf75671d1b783d7b309',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x31cbb8776e480781930f99878c5dbba51f5970c4748e5fc3d56f8b8099dfcc86'
        ),
        to_address=HexBytes('0x9954897ef12fdb2914db1fbc53153c83542f259c'),
        received_value=2867277653407089990796,
        to_chain_id=42161,
        received_time=1640366369,
        received_token=HexBytes('0xfea7a6a0b346362bf88a9e4a88416b77a57d6c2a'),
        swap_success=True,
        fee=25000000000000000000,
    )

    ret = arb_bridge_cb(log)
    assert ret == expected


def test_cb_eth_weth_out(rpcs: Dict[str, Web3]) -> None:
    log = eth_get_log(
        rpcs['ethereum'],
        '0x4eca0369ff06121550df64d26bfba3ec4b8e988fb1400c7687b62de596867406',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0xcc606833af6d4cf35f9acf4e736e290dc6e8a51d8b1b1c49241d026f18b30144'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0x3668b5b07eb210452e8fbe6c9691cdc38fc54640'),
        to_address=HexBytes('0x3668b5b07eb210452e8fbe6c9691cdc38fc54640'),
        sent_value=800000000000000000,
        received_value=None,
        pending=True,
        from_chain_id=1,
        to_chain_id=42161,
        sent_time=1640365552,
        received_time=None,
        sent_token=HexBytes('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
        received_token=HexBytes('0x82af49447d8a07e3bd95bd0d56f35241523fbab1'),
        swap_success=None,
    )

    ret = eth_bridge_cb(log)
    assert ret == expected


def test_cb_eth_gohm_out(rpcs: Dict[str, Web3]) -> None:
    log = eth_get_log(
        rpcs['ethereum'],
        '0x8bbe591d18e7294aa585e6c66f1b0e3174e65aba7c7ab5d26d49a57540f313d4',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0xf00ef1be3608a4de4edd96c6f2ec5acb78755db8c738cec30bbc497d25ead325'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0xeb2005c9a1469a88513cfdaacc4eedff24da134b'),
        to_address=HexBytes('0xeb2005c9a1469a88513cfdaacc4eedff24da134b'),
        sent_value=57298854341934152,
        received_value=None,
        pending=True,
        from_chain_id=1,
        to_chain_id=137,
        sent_time=1640360264,
        received_time=None,
        sent_token=HexBytes('0x0ab87046fbb341d058f17cbc4c1133f25a20a52f'),
        received_token=HexBytes('0xd8ca34fd379d9ca3c6ee3b3905678320f5b45195'),
        swap_success=None,
    )

    ret = eth_bridge_cb(log)
    assert ret == expected


def test_cb_eth_nusd_out(rpcs: Dict[str, Web3]) -> None:
    log = eth_get_log(
        rpcs['ethereum'],
        '0x900766dcd7e10bde90b6358b245234374dfebca7d4d544cf88ef4a38028861c6',
    )

    expected = Transaction(
        from_tx_hash=HexBytes(
            '0x3cf945b12d63bc95fba977288e1c9ac763c45eea7fd709286e2785b2d0b62d8b'
        ),
        to_tx_hash=None,
        from_address=HexBytes('0x76abc5d29977417ce881409fa0bbb5ae3ee83b72'),
        to_address=HexBytes('0x76abc5d29977417ce881409fa0bbb5ae3ee83b72'),
        sent_value=41000000,
        received_value=None,
        pending=True,
        from_chain_id=1,
        to_chain_id=56,
        sent_time=1630526543,
        received_time=None,
        sent_token=HexBytes('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'),
        received_token=HexBytes('0xe9e7cea3dedca5984780bafc599bd69add087d56'),
        swap_success=None,
    )

    ret = eth_bridge_cb(log)
    assert ret == expected


def test_cb_eth_nusd_in(rpcs: Dict[str, Web3]) -> None:
    log = eth_get_log(
        rpcs['ethereum'],
        '0xdeda50a1ff30aab8d76d6b58ff4b5a90073daf79ad09f0d397cff1983feefa46',
        log_len=2,
        idx=1,
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0xa3721577c3a09fdac583cb3c39d4e70d7b9c21b40a83012fdf11875c95faa119'
        ),
        to_address=HexBytes('0xf2172dac9059401c9e254690a478cc689681cd23'),
        received_value=2499107103118779897593,
        to_chain_id=1,
        received_time=1640341773,
        received_token=HexBytes('0x6b175474e89094c44da98b954eedeac495271d0f'),
        swap_success=True,
        fee=200000000000000000000,
    )

    ret = eth_bridge_cb(log)
    assert ret == expected
