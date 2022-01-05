#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NoReturn
import signal
import sys
import os

from dotenv import load_dotenv, find_dotenv
from psycopg.rows import dict_row
import psycopg

load_dotenv(find_dotenv('.env.sample'))
# If `.env` exists, let it override the sample env file.
load_dotenv(override=True)

if os.getenv('docker') == 'true':
    PSQL_URL = os.environ['PSQL_DOCKER_URL']
else:
    PSQL_URL = os.environ['PSQL_URL']

PSQL = psycopg.Connection.connect(PSQL_URL, row_factory=dict_row)

_sql_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_sql_path, 'get_pending_txs.sql')) as f:
    get_pending_txs_sql = f.read()

IN_SQL = """
UPDATE
    txs
SET
    (
        to_tx_hash,
        received_value,
        pending,
        received_time,
        received_token,
        swap_success
    ) = (
        %s,
        %s,
        false,
        %s,
        %s,
        %s
    )
WHERE
    kappa = %s;
"""

DEL_SQL = """
DELETE FROM
    lost_txs
WHERE
    kappa = %s;
"""

if __name__ == '__main__':
    updated = 0

    def sig_handler(*_) -> NoReturn:
        print(f'updated {updated} rows')
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)

    with PSQL.cursor() as c:
        c.execute(get_pending_txs_sql)
        print(f'able to complete {c.rowcount} rows.')

        for tx in c.fetchall():
            c.execute(
                IN_SQL,
                (tx['to_tx_hash'], tx['received_value'], tx['received_time'],
                 tx['received_token'], tx['swap_success'], tx['kappa']))
            assert c.rowcount == 1

            c.execute(DEL_SQL, (tx['kappa'], ))
            assert c.rowcount == 1

            PSQL.commit()
            updated += 1

    print(f'updated {updated} rows')
