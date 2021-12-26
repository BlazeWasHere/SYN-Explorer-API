#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from functools import partial

from web3.types import LogReceipt, FilterParams
from web3 import Web3

from explorer.utils.rpc import bridge_callback
from explorer.utils.data import SYN_DATA
from explorer.utils.data import TOPICS

POLYGON_BRIDGE_ADDRESS = Web3.toChecksumAddress(SYN_DATA['polygon']['bridge'])
MOVR_BRIDGE_ADDRESS = Web3.toChecksumAddress(SYN_DATA['moonriver']['bridge'])
ARB_BRIDGE_ADDRESS = Web3.toChecksumAddress(SYN_DATA['arbitrum']['bridge'])
ETH_BRIDGE_ADDRESS = Web3.toChecksumAddress(SYN_DATA['ethereum']['bridge'])
FTM_BRIDGE_ADDRESS = Web3.toChecksumAddress(SYN_DATA['fantom']['bridge'])
BSC_BRIDGE_ADDRESS = Web3.toChecksumAddress(SYN_DATA['bsc']['bridge'])
AVALANCHE_BRIDGE_ADDRESS = Web3.toChecksumAddress(
    SYN_DATA['avalanche']['bridge'])

_cb = partial(bridge_callback, testing=True, save_block_index=False)

bsc_bridge_cb = partial(_cb, 'bsc', BSC_BRIDGE_ADDRESS)
ftm_bridge_cb = partial(_cb, 'fantom', FTM_BRIDGE_ADDRESS)
arb_bridge_cb = partial(_cb, 'arbitrum', ARB_BRIDGE_ADDRESS)
eth_bridge_cb = partial(_cb, 'ethereum', ETH_BRIDGE_ADDRESS)
movr_bridge_cb = partial(_cb, 'moonriver', MOVR_BRIDGE_ADDRESS)
polygon_bridge_cb = partial(_cb, 'polygon', POLYGON_BRIDGE_ADDRESS)
avalanche_bridge_cb = partial(_cb, 'avalanche', AVALANCHE_BRIDGE_ADDRESS)


def _get_log(w3: Web3,
             blockhash: str,
             address: str,
             log_len: int = 1,
             idx: int = 0) -> LogReceipt:
    params: FilterParams = {
        'blockHash': blockhash,
        'address': address,
        'topics': [list(TOPICS)]  # type: ignore
    }

    log = w3.eth.get_logs(params)
    assert len(log) == log_len

    return log[idx]


eth_get_log = partial(_get_log, address=ETH_BRIDGE_ADDRESS)
arb_get_log = partial(_get_log, address=ARB_BRIDGE_ADDRESS)
bsc_get_log = partial(_get_log, address=BSC_BRIDGE_ADDRESS)
ftm_get_log = partial(_get_log, address=FTM_BRIDGE_ADDRESS)
movr_get_log = partial(_get_log, address=MOVR_BRIDGE_ADDRESS)
polygon_get_log = partial(_get_log, address=POLYGON_BRIDGE_ADDRESS)
avalanche_get_log = partial(_get_log, address=AVALANCHE_BRIDGE_ADDRESS)
