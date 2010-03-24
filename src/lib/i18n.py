# -*- coding: utf-8 -*-

__all__ = ['_', 'ngettext']

program = 'radiotray'

import locale
LC_ALL = locale.setlocale(locale.LC_ALL, '')

try:
    import gettext
    from gettext import gettext as _, ngettext
    gettext.install(program, unicode=True)
    gettext.textdomain(program)
    import __builtin__
    __builtin__.__dict__['ngettext'] = ngettext
except ImportError:
    import sys
    print >> sys.stderr, ("You don't have gettext module, no " \
        "internationalization will be used.")
    import __builtin__
    __builtin__.__dict__['_'] = lambda x: x
    __builtin__.__dict__['ngettext'] = lambda x, y, n: (n == 1) and x or y
