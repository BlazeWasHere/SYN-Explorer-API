#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import List, Callable, cast

from web3.types import LogReceipt
from gevent import Greenlet
from web3 import Web3
import gevent

from explorer.utils.data import TOPICS, SYN_DATA

# NOTE: :type:`EventData` is not really :type:`LogReceipt`,
# but close enough to assume its type.
CB = Callable[[str, str, LogReceipt], None]


def log_loop(filter, chain: str, address: str, poll: int, cb: CB):
    while True:
        # `event` is of type `EventData`.
        for event in filter.get_new_entries():
            try:
                cb(chain, address, event)
            except Exception:
                print(chain, event)
                raise

        gevent.sleep(poll)


def start(cb: CB) -> None:
    jobs: List[Greenlet] = []

    for chain, x in SYN_DATA.items():
        _address = Web3.toChecksumAddress(x['bridge'])

        filter = cast(Web3, x['w3']).eth.filter({
            'address': _address,
            'fromBlock': 'latest',
            'topics': [list(TOPICS)],
        })

        jobs.append(
            gevent.spawn(
                log_loop,
                filter,
                chain,
                _address,
                poll=2,
                cb=cb,
            ))

    # This will never sanely finish.
    gevent.joinall(jobs)
