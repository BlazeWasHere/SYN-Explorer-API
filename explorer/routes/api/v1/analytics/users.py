#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from flask import jsonify, Blueprint

from explorer.utils.analytics.users import get_unique_users_count

users_bp = Blueprint('users_bp', __name__)


# TODO: cache.
@users_bp.route('/unique', methods=['GET'])
def users_unique():
    return jsonify(get_unique_users_count())
