#
# Copyright (c) 2021 Yoichi Tanibayashi
#
__prog_name__ = 'ytani_tcpcmd'
__version__ = '0.0.0'
__author__ = 'Yoichi Tanibayashi'

from .server import server
from .client import client
from .my_logger import get_logger

all = ['server',
       'client',
       'get_logger', __prog_name__, __version__, __author__]
