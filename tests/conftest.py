#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
          Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
          https://www.boost.org/LICENSE_1_0.txt)
"""

from dotenv import find_dotenv, load_dotenv


def pytest_configure(config) -> None:
    load_dotenv(find_dotenv('.env.sample'))
    # If `.env` exists, let it override the sample env file.
    load_dotenv(override=True)
