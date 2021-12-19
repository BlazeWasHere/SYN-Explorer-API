#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
		  Copyright Blaze 2021.
 Distributed under the Boost Software License, Version 1.0.
	(See accompanying file LICENSE_1_0.txt or copy at
		  https://www.boost.org/LICENSE_1_0.txt)
"""

from gevent import monkey

# Monkey patch stuff.
monkey.patch_all()

if __name__ == '__main__':
    import explorer
    explorer.init().run(host='0.0.0.0', port=1338, debug=True)
