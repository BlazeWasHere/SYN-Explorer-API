#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from typing import (Any, List, Literal, Tuple, Generator, overload, Optional,
                    get_args)
from dataclasses import dataclass, fields
from contextlib import contextmanager
from decimal import Decimal
from attr import field

from psycopg.rows import class_row
from hexbytes import HexBytes
from psycopg import Cursor

from explorer.utils.data import PSQL, TOKEN_DECIMALS, CHAINS, TOKEN_SYMBOLS
from explorer.utils.helpers import handle_decimals


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
        # Handle token decimals.
        if 'received_token' in self.__dict__:
            chain = CHAINS[self.__dict__['to_chain_id']]
            initial = self.__dict__['received_value']
            token = self.__dict__['received_token']

            if token is not None:
                self.received_token = HexBytes(token)
                decimals = TOKEN_DECIMALS[chain][self.received_token.hex()]
                symbol = TOKEN_SYMBOLS[chain][self.received_token.hex()]

                self.received_token_symbol = symbol
                self.received_value_formatted = handle_decimals(
                    initial,
                    decimals,
                )
            else:
                self.received_token_symbol = None
                self.received_value_formatted = None

        if 'sent_token' in self.__dict__:
            chain = CHAINS[self.__dict__['from_chain_id']]
            initial = self.__dict__['sent_value']
            token = self.__dict__['sent_token']

            if token is not None:
                self.sent_token = HexBytes(token)
                decimals = TOKEN_DECIMALS[chain][self.sent_token.hex()]
                symbol = TOKEN_SYMBOLS[chain][self.sent_token.hex()]

                self.sent_token_symbol = symbol
                self.sent_value_formatted = handle_decimals(
                    initial,
                    decimals,
                )
            else:
                self.sent_token_symbol = None
                self.sent_value_formatted = None

        for field in fields(self):
            if field.name in [
                    'sent_token_symbol', 'sent_value_formatted',
                    'received_token_symbol', 'received_value_formatted'
            ]:
                continue

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
    kappa: HexBytes
    received_value_formatted: Decimal = field(init=False)
    received_token_symbol: str = field(init=False)


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
    received_token: Optional[HexBytes]
    sent_token: HexBytes
    swap_success: Optional[bool]
    kappa: HexBytes
    received_value_formatted: Optional[Decimal] = field(init=False)
    received_token_symbol: Optional[str] = field(init=False)
    sent_value_formatted: Decimal = field(init=False)
    sent_token_symbol: str = field(init=False)

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

    @staticmethod
    def fetch_recent_txs(include_pending: bool,
                         only_pending: bool,
                         limit: int = 20) -> List["Transaction"]:
        """
        Fetch the most recent transactions in the database.
        NOTE: `only_pending` is used if both options are set.
        NOTE: if either `only_pending` or `include_pending` is set, the data
            is sorted by `sent_time` rather than `received_time`.

        Args:
            include_pending (bool): Include pending transactions.
            only_pending (bool): Include only pending transactions.
        """

        sql = "SELECT * FROM txs "

        if only_pending:
            sql += "WHERE pending=true "
        elif not include_pending:
            sql += "WHERE pending=false "

        sql += "ORDER BY "
        sql += "sent_time " if (include_pending
                                or only_pending) else "received_time "
        sql += "DESC LIMIT %s;"

        with _psql_connection() as c:
            c.execute(sql, (limit, ))
            return c.fetchall()
