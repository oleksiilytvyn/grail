# -*- coding: UTF-8 -*-
"""
    run_with_watcher
    ~~~~~~~~~~~~~~~~

    Bootstrap and run Grail with File Watcher for dynamic stylesheet reloading.

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import os
import sys

from grailkit.util import application_location
from scripts.util import apply_stylesheet_watcher


def main():

    from grail.application import Grail

    os.chdir(os.path.abspath(application_location() + '/../'))

    app = Grail(sys.argv)
    apply_stylesheet_watcher(app)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
