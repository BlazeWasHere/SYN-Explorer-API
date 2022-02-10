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
        received_token=None,
        sent_token=HexBytes('0x2791bca1f2de4661ed88a30c99a7a9449aa84174'),
        swap_success=None,
        kappa=HexBytes(
            '0x46a55625f373fedd797de83417a2a7f5692d84ac039d6458f5b63ce6a189e0f6'
        ),
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
        kappa=HexBytes(
            '0x0e0b80f7b70f97f35b1b5c46d341867e09a01fe9ac053e423e78a2daecb98d5d'
        ),
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
        kappa=HexBytes(
            '0xedabb871ccd3d796d3e31bab9e543acb218b2d2e3790c8532bc60f85f7ea7e95'
        ),
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
        kappa=HexBytes(
            '0xa6b95c5a7c28a0321904a24246736e968512b09ae7b4e4f09b3f41dbbe686fca'
        ),
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
        kappa=HexBytes(
            '0xa2413fa5ca2f13ef5b483d8e603854b165186991aa17d0a5e3c38a6e3fabc514'
        ),
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
        kappa=HexBytes(
            '0x13775d055f4cf6f5b149ea563e5675489ae84c41ee47afd88408f50675fc157b'
        ),
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
        kappa=HexBytes(
            '0x902899e03f46f70bf8ee0c60bc937e78b8659be749308f4a0ae12956cc9adc6d'
        ),
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
        kappa=HexBytes(
            '0xa13a112dda8f85273bf7d05c45e49ef380697f8218d5fc77a346bf2bfb954952'
        ),
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
        received_token=None,
        sent_token=HexBytes('0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab'),
        swap_success=None,
        kappa=HexBytes(
            '0x129ae4febff07a881aee9955404ac1cb51cd7885273f6243ac75b0efafaf846d'
        ),
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
        received_token=None,
        sent_token=HexBytes('0x8f3cf7ad23cd3cadbd9735aff958023239c6a063'),
        swap_success=None,
        kappa=HexBytes(
            '0x6fbfe48e97ccbe355ce43304a5f7dfb05b67ddde7a475cf2c6829ee381f47b73'
        ),
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
        received_token=None,
        sent_token=HexBytes('0x55d398326f99059ff775485246999027b3197955'),
        swap_success=None,
        kappa=HexBytes(
            '0xd58c0a753235da2aa997250f9bb6b27cc5678f5f247e5e2336992346acf75e00'
        ),
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
        kappa=HexBytes(
            '0xb3c7ec533fbaeff3a78eae5a36198c3b2a32e2eaa4d476e8a11708c1e483d6a9'
        ),
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
        received_token=None,
        sent_token=HexBytes('0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'),
        swap_success=None,
        kappa=HexBytes(
            '0xa26cb5ed38268297851668a86fecc925b4c5c2679a9becfd646c7da90cf2bdd2'
        ),
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
        received_token=None,
        sent_token=HexBytes('0x0ab87046fbb341d058f17cbc4c1133f25a20a52f'),
        swap_success=None,
        kappa=HexBytes(
            '0x6d4cefc52bc7ea5e1ee62b3266c6f00b2b4551f905a98fa4f3d17bafea860a81'
        ),
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
        received_token=None,
        sent_token=HexBytes('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'),
        swap_success=None,
        kappa=HexBytes(
            '0x43a799ca7838f79dd23097090481db9bfc3e0421d85277a197b0af3d502b3a76'
        ),
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
        kappa=HexBytes(
            '0x2caf7c0ca2c3babbca48d7d2bda7913d68ba84b81a6312e06d38f6897131b49e'
        ),
    )

    ret = eth_bridge_cb(log)
    assert ret == expected


def test_cb_arb_usdc_in_3pool(rpcs: Dict[str, Web3]) -> None:
    log = arb_get_log(
        rpcs['arbitrum'],
        '0xdd4b949c3d1adaad6c51ff6e237db890b461e7eeb89f19e72c0e7daa1748e874',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0xf40fb113d8a90afa07877a5a8e697b7b6b4a1c42cce9628d15f6e9b279903b8d'
        ),
        to_address=HexBytes('0x709ff5d28cb0233b086eabd6d641cbf823d4566e'),
        received_value=139833175,
        to_chain_id=42161,
        received_time=1643652905,
        received_token=HexBytes('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8'),
        swap_success=True,
        kappa=HexBytes(
            '0x0fb1b5ec733b3877d30e67c37818ab62531b349fa3e68d359696b87a6cc999ad'
        ),
    )

    ret = arb_bridge_cb(log)
    assert ret == expected


def test_cb_ftm_usdc_in_3pool(rpcs: Dict[str, Web3]) -> None:
    log = ftm_get_log(
        rpcs['fantom'],
        '0x00012de400000bd539f3e0e67da4103dea44167b3728e36fc616458104715754')

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0xbb2f9787585a1e949f19abe22e17c462edc240f3db9464bdcc1a12c4e7157f2b'
        ),
        to_address=HexBytes('0xb191ba274502357bbad683a3a4cc4bf1b63e0d65'),
        received_value=48032688,
        to_chain_id=250,
        received_time=1643660740,
        received_token=HexBytes('0x04068da6c83afcfa0e13ba15a6696662335d5b75'),
        swap_success=True,
        kappa=HexBytes(
            '0x9eb58cf15d416ec03ce19d633024396fc82bacf2d0e099cc551bf3c4be06175e'
        ),
    )

    ret = ftm_bridge_cb(log)
    assert ret == expected


def test_cb_avalanche_gmx_in(rpcs: Dict[str, Web3]) -> None:
    log = avalanche_get_log(
        rpcs['avalanche'],
        '0x38d5b3b9ccf63c6de79ebbad63253f8e9e87a0ccfbbf8e8a2edf506ba4b572f5',
    )

    expected = LostTransaction(
        to_tx_hash=HexBytes(
            '0x5d4541cc14d1a7f7e22b1ba544aadaa3c07bfd3fe225b47530c0962c7f0b5e0a'
        ),
        to_address=HexBytes('0x300e780479437092cd0a40a6f3b7eae5dcd33226'),
        received_value=200030000000000000000,
        to_chain_id=43114,
        received_time=1644274055,
        received_token=HexBytes('0x62edc0692bd897d2295872a9ffcac5425011c661'),
        swap_success=None,
        kappa=HexBytes(
            '0x7782b444e289e959d25880fac4472fad55eab4f5b4192f63063b81ae38fc8715'
        ),
    )

    ret = avalanche_bridge_cb(log)
    assert ret == expected
