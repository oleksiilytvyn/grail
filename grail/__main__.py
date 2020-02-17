# -*- coding: UTF-8 -*-
"""
    grail.__main__
    ~~~~~~~~~~~~~~

    Run Grail as python package

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""

import os
import sys

from grailkit.util import application_location
from grail.application import Grail


if __name__ == "__main__":

    os.chdir(application_location())

    app = Grail(sys.argv)
    sys.exit(app.exec_())
