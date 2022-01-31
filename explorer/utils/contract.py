#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import Optional, List, Any, Union, Literal
from dataclasses import dataclass
from hexbytes import HexBytes

import web3.exceptions
from web3 import Web3


@dataclass
class TokenInfo:
    chain_id: int
    address: HexBytes
    decimals: int
    max_swap: int
    min_swap: int
    swap_fee: int
    min_swap_fee: int
    max_swap_fee: int
    has_underlying: bool
    is_underlying: bool


# TODO(blaze): better type hints.
def call_abi(data, key: str, func_name: str, *args, **kwargs) -> Any:
    call_args = kwargs.pop('call_args', {})
    return getattr(data[key].functions, func_name)(*args,
                                                   **kwargs).call(**call_args)


def get_all_tokens_in_pool(chain: str,
                           max_index: Optional[int] = None,
                           func: str = 'nusdpool_contract') -> List[str]:
    """
    Get all tokens by calling `getToken` by iterating from 0 till a
    contract error or `max_index` and implicitly sorted by index.

    Args:
        chain (str): the EVM chain
        max_index (Optional[int], optional): max index to iterate to. 
            Defaults to None.

    Returns:
        List[str]: list of token addresses
    """
    from explorer.utils.data import SYN_DATA, MAX_UINT8

    assert (chain in SYN_DATA)

    data = SYN_DATA[chain]
    res: List[str] = []

    for i in range(max_index or MAX_UINT8):
        try:
            res.append(call_abi(data, func, 'getToken', i))
        except (web3.exceptions.ContractLogicError,
                web3.exceptions.BadFunctionCallOutput):
            # Out of range.
            break

    return res


def get_bridge_token_info(chain_id: int,
                          _id: str) -> Union[Literal[False], TokenInfo]:
    from explorer.utils.data import BRIDGE_CONFIG

    func = BRIDGE_CONFIG.get_function_by_signature('getToken(string,uint256)')
    ret = func(_id, chain_id).call()

    # Does not exist - function's default ret.
    if ret == (0, '0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0,
               0, False, False):
        return False

    return TokenInfo(*ret)


def bridge_token_to_id(chain_id: int, token: HexBytes) -> str:
    from explorer.utils.data import BRIDGE_CONFIG

    return BRIDGE_CONFIG.functions.getTokenID(token, chain_id).call()
