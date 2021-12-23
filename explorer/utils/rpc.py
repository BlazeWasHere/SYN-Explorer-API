#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import Callable, Dict, cast, List
import time

from web3.exceptions import LogTopicError, MismatchedABI
from web3.types import FilterParams, LogReceipt
from psycopg.errors import UniqueViolation
from hexbytes import HexBytes
from web3 import Web3
import gevent

from explorer.utils.data import BRIDGE_ABI, CHAINS, OLDBRIDGE_ABI, PSQL, \
    SYN_DATA, LOGS_REDIS_URL, OLDERBRIDGE_ABI, TOKENS_IN_POOL, TOKENS_INFO, \
    TOPICS, TOPIC_TO_EVENT, TRANSFER_ABI, Direction, CHAINS_REVERSED
from explorer.utils.helpers import convert, address_to_pool, search_logs, \
    retry

# Start blocks of the 4pool ~>=Nov-7th-2021 apart from ethereum.
_start_blocks = {
    'ethereum': 13136427,  # nUSD pool
    'arbitrum': 2876718,  # nUSD pool
    'avalanche': 6619002,  # nUSD pool
    'bsc': 12431591,  # nUSD pool
    'fantom': 21297076,  # nUSD Pool
    'polygon': 21071348,  # nUSD pool
    'harmony': 19163634,  # nUSD pool
    'boba': 16221,  # nUSD pool
    'moonriver': 890949,
    'optimism': 30819,  # nETH pool
}

MAX_BLOCKS = 5000

OUT_SQL = """
INSERT into
    txs (
        from_tx_hash,
        from_address,
        to_address,
        sent_value,
        from_chain_id,
        to_chain_id,
        sent_time,
        sent_token,
        received_token
    )
VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

IN_SQL = """
UPDATE
    txs
SET
    (
        to_tx_hash,
        received_value,
        pending,
        received_time,
        swap_success
    ) = (
        %s,
        %s,
        false,
        %s,
        %s
    )
WHERE
    to_address = %s
    AND pending = true
    AND received_token = %s
    AND to_chain_id = %s;
"""

LOST_IN_SQL = """
INSERT into
    lost_txs (
        to_tx_hash,
        to_address,
        received_value,
        to_chain_id,
        received_time,
        received_token,
        swap_success,
        fee
    )
VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s);
"""


# REF: https://github.com/synapsecns/synapse-contracts/blob/master/contracts/bridge/SynapseBridge.sol#L63-L129
def bridge_callback(chain: str,
                    address: str,
                    log: LogReceipt,
                    abi: str = BRIDGE_ABI) -> None:
    w3: Web3 = SYN_DATA[chain]['w3']
    contract = w3.eth.contract(w3.toChecksumAddress(address), abi=abi)
    tx_hash = log['transactionHash']

    timestamp = w3.eth.get_block(
        log['blockNumber'])['timestamp']  # type: ignore
    tx_info = w3.eth.get_transaction(tx_hash)
    from_chain = CHAINS_REVERSED[chain]
    # Default value of 'nusd', although it gets overwritten later on.
    pool = 'nusd'

    # The info before wrapping the asset can be found in the receipt.
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash,
                                                  timeout=10,
                                                  poll_latency=0.5)
    do_search_logs = True

    topic = cast(str, convert(log['topics'][0]))
    if topic not in TOPICS:
        raise RuntimeError(f'sanity check? got invalid topic: {topic}')

    event = TOPIC_TO_EVENT[topic]
    direction = TOPICS[topic]

    if direction == Direction.OUT:
        # Info is stored in the first log.
        _log = receipt['logs'][0]
        _token = w3.eth.contract(_log['address'], abi=TRANSFER_ABI)

        # For OUT transactions the bridged asset
        # and its amount are stored in the logs data
        try:
            data = contract.events[event]().processLog(log)
        except LogTopicError:
            if abi == OLDERBRIDGE_ABI:
                raise TypeError(log, chain)
            elif abi == OLDBRIDGE_ABI:
                abi = OLDERBRIDGE_ABI
            elif abi == BRIDGE_ABI:
                abi = OLDBRIDGE_ABI
            else:
                raise RuntimeError(f'sanity check? got invalid abi: {abi}')

            return bridge_callback(chain, address, log, abi)

        args = data['args']  # type: ignore
        to_chain = CHAINS[args['chainId']]

        if 'pool' in args:
            # Some pools during testing - disregard these txs.
            if ('0xa9E90579eb086bcdA910dD94041ffE041Fb4aC89' == args['pool']
                    and chain == 'optimism'):
                return
            elif ('0x11dB9cb06f98fA2bE027589B5D5734ca0D4E46BA' == args['pool']
                  and chain == 'boba'):
                return
            pool = address_to_pool(chain, args['pool'])
        else:
            # Find out if its an '*ETH' token.
            if 'token' in args:
                token = args['token'].lower()
                if 'eth' in TOKENS_INFO[chain][token]['symbol'].lower():
                    pool = 'neth'

        pool_tokens = TOKENS_IN_POOL[to_chain][pool]

        if event not in [
                'TokenRedeem',
                'TokenRedeemAndRemove',
                'TokenDeposit',
                'TokenDepositAndSwap',
        ]:
            received_token = pool_tokens[args['tokenIndexTo']]
            sent_token = _log['address']
        elif event in ['TokenRedeem', 'TokenDeposit', 'TokenDepositAndSwap']:
            received_token = sent_token = args['token']

            if event == 'TokenDepositAndSwap':
                if 'ETH' in TOKENS_INFO[chain][sent_token.lower()]['name']:
                    pool_tokens = TOKENS_IN_POOL[to_chain]['neth']

                received_token = pool_tokens[args['tokenIndexTo']]

            do_search_logs = False
        elif event == 'TokenRedeemAndRemove':
            received_token = pool_tokens[args['swapTokenIndex']]
            sent_token = args['token']
        else:
            raise RuntimeError(
                f'did not converge on OUT, {event}, {tx_hash.hex()}, {chain}')

        if do_search_logs:
            try:
                _data = _token.events['Transfer']().processLog(_log)['args']
            except MismatchedABI:
                # Info was not stored in the first log :/
                _data = search_logs(w3, receipt, sent_token)
                if _data is None:
                    raise RuntimeError(
                        f'did not converge OUT, {event} {chain} {tx_hash.hex()}'
                        f' receipt: {receipt}\n{args} {sent_token}')

            value = _data['value']
        else:
            value = args['amount']

        with PSQL.connection() as conn:
            conn.autocommit = True
            with conn.cursor() as c:
                c.execute(OUT_SQL, (
                    tx_hash,
                    HexBytes(tx_info['from']),
                    HexBytes(args['to']),
                    value,
                    from_chain,
                    args['chainId'],
                    timestamp,
                    HexBytes(sent_token),
                    HexBytes(received_token),
                ))
    elif direction == Direction.IN:
        # For IN transactions the bridged asset
        # and its amount are stored in the tx.input
        # All IN transactions are guaranteed to be
        # from validators to Bridge contract
        _, args = contract.decode_function_input(
            tx_info['input'])  # type: ignore

        swap_success = args.get('swapSuccess', None)

        if 'pool' in args:
            # Some pools during testing - disregard these txs.
            if ('0xa9E90579eb086bcdA910dD94041ffE041Fb4aC89' == args['pool']
                    and chain == 'optimism'):
                return
            elif ('0x11dB9cb06f98fA2bE027589B5D5734ca0D4E46BA' == args['pool']
                  and chain == 'boba'):
                return

            pool = address_to_pool(chain, args['pool'])

        if event not in [
                'TokenWithdraw', 'TokenMint', 'TokenWithdrawAndRemove'
        ]:
            received_token = TOKENS_IN_POOL[chain][pool][args['tokenIndexTo']]
        elif event == 'TokenWithdrawAndRemove':
            received_token = TOKENS_IN_POOL[chain][pool][
                args['swapTokenIndex']]
        else:
            received_token = args['token']
            do_search_logs = False

        if do_search_logs:
            _data = search_logs(w3, receipt, received_token)
            if _data is None or not swap_success:
                # Sometimes swap fails and the user received a nexus asset
                # instead, so search for the nexus asset (nETH, nUSD).
                if chain == 'ethereum':
                    # Nexus assets aren't in eth pools.
                    received_token = '0x1b84765de8b7566e4ceaf4d0fd3c5af52d3dde4f'
                else:
                    received_token = TOKENS_IN_POOL[chain][pool][0]

                _data = search_logs(w3, receipt, received_token)
                if _data is None:
                    raise RuntimeError(
                        f'did not converge IN, {event} {chain} {tx_hash.hex()}'
                        f' receipt: {receipt}\n{args} {received_token}')

            value = str(_data['value'])
        else:
            value = args['amount']

        with PSQL.connection() as conn:
            conn.autocommit = True
            with conn.cursor() as c:
                run_lost_sql = False
                params = (
                    tx_hash,
                    value,
                    timestamp,
                    swap_success,
                    HexBytes(args['to']),
                    HexBytes(received_token),
                    from_chain,
                )

                try:
                    c.execute(IN_SQL, params)
                except:
                    run_lost_sql = True
                    raise
                finally:
                    # No rows got updated: means that there was no
                    # corresponding OUT tx.
                    if c.rowcount == 0 or run_lost_sql:
                        c.execute(
                            LOST_IN_SQL,
                            (tx_hash, HexBytes(args['to']), value, from_chain,
                             timestamp, HexBytes(received_token), swap_success,
                             str(args['fee'])))
                    else:
                        if c.rowcount != 1:
                            raise RuntimeError(
                                f'{c._last_query} | {params} affected '
                                f'{c.rowcount} not 1')

    else:
        raise RuntimeError(f'sanity check? got {direction}')

    LOGS_REDIS_URL.set(f'{chain}:logs:{address}:MAX_BLOCK_STORED',
                       log['blockNumber'])
    LOGS_REDIS_URL.set(f'{chain}:logs:{address}:TX_INDEX',
                       log['transactionIndex'])


def get_logs(
    chain: str,
    callback: Callable[[str, str, LogReceipt], None],
    address: str,
    start_block: int = None,
    till_block: int = None,
    max_blocks: int = MAX_BLOCKS,
    topics: List[str] = list(TOPICS),
    key_namespace: str = 'logs',
    start_blocks: Dict[str, int] = _start_blocks,
) -> None:
    w3: Web3 = SYN_DATA[chain]['w3']
    _chain = f'[{chain}]'
    chain_len = max(len(c) for c in SYN_DATA) + 2
    tx_index = -1

    if start_block is None:
        _key_block = f'{chain}:{key_namespace}:{address}:MAX_BLOCK_STORED'
        _key_index = f'{chain}:{key_namespace}:{address}:TX_INDEX'

        if (ret := LOGS_REDIS_URL.get(_key_block)) is not None:
            start_block = max(int(ret), start_blocks[chain])

            if (ret := LOGS_REDIS_URL.get(_key_index)) is not None:
                tx_index = int(ret)
        else:
            start_block = start_blocks[chain]

    if till_block is None:
        till_block = w3.eth.block_number

    print(
        f'{key_namespace} | {_chain:{chain_len}} starting from {start_block} '
        f'with block height of {till_block}')

    jobs: List[gevent.Greenlet] = []
    _start = time.time()
    x = 0

    total_events = 0
    initial_block = start_block

    while start_block < till_block:
        to_block = min(start_block + max_blocks, till_block)

        params: FilterParams = {
            'fromBlock': start_block,
            'toBlock': to_block,
            'address': w3.toChecksumAddress(address),
            'topics': [topics],  # type: ignore
        }

        logs: List[LogReceipt] = w3.eth.get_logs(params)
        for log in logs:
            # Skip transactions from the very first block
            # that are already in the DB
            if log['blockNumber'] == initial_block \
              and log['transactionIndex'] <= tx_index:
                continue

            retry(callback, chain, address, log)

        start_block += max_blocks + 1

        y = time.time() - _start
        total_events += len(logs)

        percent = 100 * (to_block - initial_block) \
            / (till_block - initial_block)

        print(f'{key_namespace} | {_chain:{chain_len}} elapsed {y:5.1f}s'
              f' ({y - x:5.1f}s), found {total_events:5} events,'
              f' {percent:4.1f}% done: so far at block {start_block}')
        x = y

    gevent.joinall(jobs)
    print(f'{_chain:{chain_len}} it took {time.time() - _start:.1f}s!')
