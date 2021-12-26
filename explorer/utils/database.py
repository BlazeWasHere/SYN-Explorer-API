#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import Any, List, Literal, Tuple, Generator, overload, Optional, \
    get_args
from dataclasses import dataclass, fields
from contextlib import contextmanager

from psycopg.rows import class_row
from hexbytes import HexBytes
from psycopg import Cursor

from explorer.utils.data import PSQL


class NotFoundInDatabase(Exception):
    def __init__(self, value: Any, db: str = 'txs') -> None:
        self.message = f'{value!r} was not found in db {db!r}'
        super().__init__(self.message)


@contextmanager
def _psql_connection() -> Generator[Cursor['Transaction'], None, None]:
    with PSQL.connection() as conn:
        with conn.cursor(row_factory=class_row(Transaction)) as c:
            yield c


class Base:
    def __post_init__(self) -> None:
        for field in fields(self):
            val = self.__dict__[field.name]

            # Pscyopg returns psql's bytea as bytes.
            if type(val) == bytes:
                self.__dict__[field.name] = HexBytes(val)
            # We store ints as varchars in psql due to BIGINT's limitations.
            elif type(val) == str and (field.type == int
                                       or get_args(field.type)[0] == int):
                self.__dict__[field.name] = int(val)
            elif not isinstance(val, get_args(field.type) or field.type):
                raise TypeError(f'expected {field.name!r} to be of type '
                                f'{field.type} not {type(val)}')


@dataclass
class LostTransaction(Base):
    to_tx_hash: HexBytes
    to_address: HexBytes
    received_value: int
    to_chain_id: int
    received_time: int
    received_token: HexBytes
    swap_success: Optional[bool]
    fee: int


@dataclass
class Transaction(Base):
    from_tx_hash: HexBytes
    to_tx_hash: Optional[HexBytes]
    from_address: HexBytes
    to_address: HexBytes
    sent_value: int
    received_value: Optional[int]
    pending: bool
    from_chain_id: int
    to_chain_id: int
    sent_time: int
    received_time: Optional[int]
    sent_token: HexBytes
    received_token: Optional[HexBytes]
    swap_success: Optional[bool]

    @staticmethod
    def search(column: str, value: Any) -> List["Transaction"]:
        with _psql_connection() as c:
            c.execute("SELECT * FROM txs WHERE %s = %s", (column, value))
            return c.fetchall()

    @overload
    @staticmethod
    def search_with_tx_hash(
            tx_hash: HexBytes) -> Tuple['Transaction', Literal['to', 'from']]:
        ...

    @overload
    @staticmethod
    def search_with_tx_hash(
            tx_hash: HexBytes, silent: bool
    ) -> Optional[Tuple['Transaction', Literal['to', 'from']]]:
        ...

    @staticmethod
    def search_with_tx_hash(
        tx_hash: HexBytes,
        silent: bool = False
    ) -> Optional[Tuple['Transaction', Literal['to', 'from']]]:
        """
        Find the data stored in the database relating to `tx_hash`, looking
        through both columns: `from_tx_hash` and `to_tx_hash`.
        """

        sql = """
           SELECT * FROM txs
           WHERE
                from_tx_hash = %(tx_hash)s
                OR to_tx_hash = %(tx_hash)s;
            """

        with _psql_connection() as c:
            c.execute(sql, {'tx_hash': tx_hash})
            ret = c.fetchone()

            if ret is None:
                if not silent:
                    raise NotFoundInDatabase(tx_hash)

                return None

            if ret.to_tx_hash == tx_hash:
                direction = 'to'
            elif ret.from_tx_hash == tx_hash:
                direction = 'from'
            else:
                raise RuntimeError(
                    f'sanity check: {tx_hash} does not match any at {ret!r}')

        return ret, direction

    @overload
    @staticmethod
    def search_with_address(address: HexBytes) -> List['Transaction']:
        ...

    @overload
    @staticmethod
    def search_with_address(address: HexBytes,
                            silent: bool) -> Optional[List['Transaction']]:
        ...

    @staticmethod
    def search_with_address(
            address: HexBytes,
            silent: bool = False) -> Optional[List['Transaction']]:
        """
        Find the data stored in the database relating to `tx_hash`, looking
        through both columns: `from_address` and `to_address`.
        """

        sql = """
           SELECT * FROM txs
           WHERE
                from_address = %(address)s
                OR to_address = %(address)s;
            """

        with _psql_connection() as c:
            c.execute(sql, {'address': address})
            ret = c.fetchall()

            if not ret:
                if not silent:
                    raise NotFoundInDatabase(address)

                return None

        return ret
