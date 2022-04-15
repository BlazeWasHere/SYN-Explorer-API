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


def get_unique_users_count(from_time: int = None, to_time: int = None) -> int:
    """
    Get unique users with the option to filter by `received_time` using UNIX
    timestamps - `int(time.time())`

    Args:
        from_time (int, optional): received_time gt than `from_time`.
        to_time (int, optional): received_time lt than `to_time`.

    Returns:
        int: number of unique users
    """

    sql = "SELECT COUNT(DISTINCT from_address) FROM txs "
    params = []

    if from_time or to_time:
        sql += "WHERE received_time "

    if from_time:
        params.append(from_time)
        sql += "> %s "

    if to_time:
        params.append(to_time)

        if from_time:
            sql += "AND received_time "

        sql += "< %s "

    with PSQL.connection() as conn:
        with conn.cursor() as c:
            c.execute(sql, params)
            ret = c.fetchone()
            assert ret is not None

            return cast(int, ret[0])
