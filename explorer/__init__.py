#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from gevent import monkey
import gevent

# Monkey patch stuff.
monkey.patch_all()

from math import log2

from werkzeug.routing import BaseConverter, Map
from web3._utils import request
from hexbytes import HexBytes
import simplejson as json
from flask import Flask
import lru

from explorer.utils.helpers import dispatch_get_logs
from explorer.utils.data import SYN_DATA, TESTING
from explorer.utils.database import Transaction
from explorer.utils.rpc import bridge_callback
from explorer.utils import poll

# Get the next ^2 that is greater than len(SYN_DATA.keys()) so we can make
# the cache size greater than the amount of chains we support.
n = 1 << int(log2(len(SYN_DATA.keys()))) + 1

b = request._session_cache.get_size()
request._session_cache.set_size(n)
c = request._session_cache.get_size()
assert b != c, '_session_cache size did not change'
assert c == n, 'new _session_cache size is not what we set it to'

if not TESTING:
    gevent.spawn(poll.start, bridge_callback)
    gevent.spawn(dispatch_get_logs, bridge_callback)


class HexConverter(BaseConverter):
    def __init__(self, map: "Map", length: int = 64) -> None:
        super().__init__(map)
        self.regex = f"0x([A-Fa-f0-9]{{{length}}})$"

    def to_python(self, value: str) -> HexBytes:
        return HexBytes(value)

    def to_url(self, value: HexBytes) -> str:
        return value.hex()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Transaction):
            return {
                k: v.hex() if isinstance(v, HexBytes) else v
                for k, v in o.__dict__.items()
            }
        elif isinstance(o, int):
            # Over max `Number.MAX_SAFE_INTEGER` for JS.
            if o > (2**53 - 1):
                return str(o)

        super().default(o)


def init() -> Flask:
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder  # type: ignore
    app.json_decoder = json.JSONDecoder  # type: ignore

    app.url_map.converters['hex'] = HexConverter

    from .routes.api.v1.analytics.users import users_bp
    from .routes.api.v1.search import search_bp
    from .routes.root import root_bp

    app.register_blueprint(root_bp)
    app.register_blueprint(search_bp, url_prefix='/api/v1/search')
    app.register_blueprint(users_bp, url_prefix='/api/v1/analytics/users')

    return app
