#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
		  Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
	(See accompanying file LICENSE_1_0.txt or copy at
		  https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import List, Dict, Optional, TypeVar, Union, cast, Literal, Any, \
    Callable
import traceback
import decimal
import logging

from web3.types import _Hash32, TxReceipt, LogReceipt
from web3.exceptions import MismatchedABI
from hexbytes import HexBytes
from gevent import Greenlet
from web3.main import Web3
import gevent

from .data import SYN_DATA, TOKEN_DECIMALS, POOLS, TRANSFER_ABI

logger = logging.Logger(__name__)
D = decimal.Decimal
KT = TypeVar('KT')
VT = TypeVar('VT')
T = TypeVar('T')


def convert(value: T) -> Union[T, str, List]:
    if isinstance(value, HexBytes):
        return value.hex()
    elif isinstance(value, list):
        return [convert(item) for item in value]
    else:
        return value


def get_gas_stats_for_tx(chain: str,
                         w3: Web3,
                         txhash: _Hash32,
                         receipt: TxReceipt = None) -> Dict[str, D]:
    if receipt is None:
        receipt = w3.eth.get_transaction_receipt(txhash)

    # Arbitrum has this crazy gas bidding system, this isn't some
    # sort of auction now is it?
    if chain == 'arbitrum':
        paid = receipt['feeStats']['paid']  # type: ignore
        paid_for_gas = 0

        for key in paid:
            paid_for_gas += hex_to_int(paid[key])

        gas_price = D(paid_for_gas) / (D(1e9) * D(receipt['gasUsed']))

        return {
            'gas_paid': handle_decimals(paid_for_gas, 18),
            'gas_price': gas_price
        }

    ret = w3.eth.get_transaction(txhash)

    # Optimism seems to be pricing gas on both L1 and L2,
    # so we aggregate these and use gas_spent on L1 to
    # determine the "gas price", as L1 gas >>> L2 gas
    if chain == 'optimism':
        paid_for_gas = receipt['gasUsed'] * ret['gasPrice']  # type: ignore
        paid_for_gas += hex_to_int(receipt['l1Fee'])  # type: ignore
        gas_used = hex_to_int(receipt['l1GasUsed'])  # type: ignore
        gas_price = D(paid_for_gas) / (D(1e9) * D(gas_used))

        return {
            'gas_paid': handle_decimals(paid_for_gas, 18),
            'gas_price': gas_price
        }

    gas_price = handle_decimals(ret['gasPrice'], 9)  # type: ignore

    return {
        'gas_paid': handle_decimals(gas_price * receipt['gasUsed'], 9),
        'gas_price': gas_price
    }


def convert_amount(chain: str, token: str, amount: int) -> D:
    try:
        return handle_decimals(amount, TOKEN_DECIMALS[chain][token.lower()])
    except KeyError:
        logger.warning(f'return amount 0 for token {token} on {chain}')
        return D(0)


def hex_to_int(str_hex: str) -> int:
    """
    Convert 0xdead1234 into integer
    """
    return int(str_hex[2:], 16)


def handle_decimals(num: Union[str, int, float, D],
                    decimals: int,
                    *,
                    precision: int = None) -> D:
    if type(num) != D:
        num = str(num)

    res: D = D(num) / D(10**decimals)

    if precision is not None:
        return res.quantize(D(10)**-precision)

    return res


def is_in_range(value: int, min: int, max: int) -> bool:
    return min <= value <= max


def get_airdrop_value_for_block(ranges: Dict[float, List[Optional[int]]],
                                block: int) -> D:
    def _transform(num: float) -> D:
        return D(str(num))

    for airdrop, _ranges in ranges.items():
        # `_ranges` should have a [0] (start) and a [1] (end)
        assert len(_ranges) == 2, f'expected {_ranges} to have 2 items'

        _min: int
        _max: int

        # Has always been this airdrop value.
        if _ranges[0] is None and _ranges[1] is None:
            return _transform(airdrop)
        elif _ranges[0] is None:
            _min = 0
            _max = cast(int, _ranges[1])

            if is_in_range(block, _min, _max):
                return _transform(airdrop)
        elif _ranges[1] is None:
            _min = _ranges[0]

            if _min <= block:
                return _transform(airdrop)
        else:
            _min, _max = cast(List[int], _ranges)

            if is_in_range(block, _min, _max):
                return _transform(airdrop)

    raise RuntimeError('did not converge', block, ranges)


def address_to_pool(chain: str, address: str) -> Literal['nusd', 'neth']:
    for k, v in POOLS[chain].items():
        if v.lower() == address.lower():
            return k

    raise RuntimeError(f"{address} not found in {chain}'s pools")


def search_logs(w3: Web3,
                receipt: TxReceipt,
                received_token: str,
                abi: str = TRANSFER_ABI) -> Optional[Dict[str, Any]]:
    for x in receipt['logs']:
        if x['address'].lower() == received_token.lower():
            token = w3.eth.contract(x['address'], abi=abi)

            try:
                return token.events['Transfer']().processLog(x)['args']
            except MismatchedABI:
                continue


def dispatch_get_logs(
    cb: Callable[[str, str, LogReceipt], None],
    topics: List[str] = None,
    key_namespace: str = 'logs',
    address_key: str = 'bridge',
    join_all: bool = True,
) -> Optional[List[Greenlet]]:
    from explorer.utils.rpc import get_logs, TOPICS

    topics = topics or list(TOPICS)
    jobs: List[Greenlet] = []

    for chain in SYN_DATA:
        address = SYN_DATA[chain][address_key]

        if chain in [
                'harmony',
                'ethereum',
                'moonriver',
        ]:
            jobs.append(
                gevent.spawn(get_logs,
                             chain,
                             cb,
                             address,
                             max_blocks=1024,
                             topics=topics,
                             key_namespace=key_namespace))
        elif chain in ['boba', 'bsc']:
            jobs.append(
                gevent.spawn(get_logs,
                             chain,
                             cb,
                             address,
                             max_blocks=512,
                             topics=topics,
                             key_namespace=key_namespace))
        elif chain == 'polygon':
            jobs.append(
                gevent.spawn(get_logs,
                             chain,
                             cb,
                             address,
                             max_blocks=2048,
                             topics=topics,
                             key_namespace=key_namespace))
        else:
            jobs.append(
                gevent.spawn(get_logs,
                             chain,
                             cb,
                             address,
                             topics=topics,
                             key_namespace=key_namespace))

    if join_all:
        gevent.joinall(jobs)
    else:
        return jobs


def retry(func: Callable[..., T], *args, **kwargs) -> Optional[T]:
    attempts = kwargs.pop('attempts', 3)

    for _ in range(attempts):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(f'retry attempt {_}, args: {args}')
            traceback.print_exc()
            gevent.sleep(2**_)

    logging.critical(f'maximum retries ({attempts}) reached')
