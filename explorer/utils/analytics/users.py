#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import cast

from explorer.utils.data import PSQL


def get_unique_users_count() -> int:
    with PSQL.connection() as conn:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(DISTINCT from_address) from txs;")
            ret = c.fetchone()
            assert ret is not None

            return cast(int, ret[0])
