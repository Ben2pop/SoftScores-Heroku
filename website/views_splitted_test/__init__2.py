# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from future import standard_library

from website.views.base_views import *
from website.views.chart_views import *
from website.views.algo_views import *


standard_library.install_aliases()
