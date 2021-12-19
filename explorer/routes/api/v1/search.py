#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from flask import jsonify, Blueprint
from hexbytes import HexBytes

from explorer.utils.database import Transaction

search_bp = Blueprint('search_bp', __name__)


# TODO: cache w/ redis-cache
@search_bp.route('/txhash/<hex:txhash>', methods=['GET'])
def search_txhash(txhash: HexBytes):
    ret = Transaction.search_with_tx_hash(txhash, silent=True)

    if ret is None:
        return jsonify(None), 404

    return jsonify(ret[0])


@search_bp.route('/address/<hex(length=40):address>', methods=['GET'])
def search_address(address: HexBytes):
    ret = Transaction.search_with_address(address, silent=True)

    if ret is None:
        return jsonify(None), 404

    return jsonify(ret)
