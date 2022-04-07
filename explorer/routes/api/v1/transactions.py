#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from flask import jsonify, Blueprint, request
from typing import Optional
from hexbytes import HexBytes
from explorer.utils.database import Transaction

transactions_bp = Blueprint('transactions_bp', __name__)


@transactions_bp.route('/recent', methods=['GET'])
def search_recent_txs():
    include_pending = request.args.get('include_pending', False, bool)
    only_pending = request.args.get('only_pending', False, bool)
    limit = request.args.get('limit', 20, int)

    if limit > 250:
        return jsonify({'error': 'limit must be less than 250'}), 400
    elif limit < 0:
        return jsonify({'error': 'limit must be positive'}), 400

    ret = Transaction.fetch_recent_txs(include_pending, only_pending, limit)

    return jsonify(ret)


@transactions_bp.route('/', methods=['GET'])
def search():
    from_chain_id: Optional[int] = request.args.get('from_chain_id', None, int)
    to_chain_id: Optional[int] = request.args.get('to_chain_id', None, int)
    from_tx_hash: Optional[HexBytes] = request.args.get('from_tx_hash', None, HexBytes)
    to_tx_hash: Optional[HexBytes] = request.args.get('to_tx_hash', None, HexBytes)
    kappa: Optional[HexBytes] = request.args.get('kappa', None, HexBytes)
    offset: Optional[int] = request.args.get('offset', 0, int)

    ret = Transaction.generic_search(
        offset=offset,
        args={
            "from_chain_id": from_chain_id,
            "to_chain_id": to_chain_id,
            "from_tx_hash": from_tx_hash,
            "to_tx_hash": to_tx_hash,
            "kappa": kappa
        }
    )

    if ret is None:
        return jsonify(None), 404

    return jsonify(ret)
