#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from flask import jsonify, Blueprint, request

from explorer.utils.database import Transaction

transactions_bp = Blueprint('transactions_bp', __name__)


@transactions_bp.route('/recent', methods=['GET'])
def search_recent_txs():
    include_pending = request.args.get('include_pending', False, bool)
    only_pending = request.args.get('only_pending', False, bool)
    limit = request.args.get('limit', 20, int)

    if limit > 250:
        return jsonify({'error': 'limit must be less than 250'}, 400)

    ret = Transaction.fetch_recent_txs(include_pending, only_pending, limit)

    return jsonify(ret)
