#
# Copyright (c) 2021 Yoichi Tanibayashi
#
import socketserver
import socket
import threading
import queue
import json
import time
import click
from .my_logger import get_logger


class Server:
    """ Server """

    __log = get_logger(__name__, False)

    DEF_PORT = 12345

    def __init__(self, debug=False):
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)

    def server(self, arg1):
        """ method1 """
        self.__log.debug('arg=%s', arg1)

        print('Hello, %s' % (arg1))


class ServerApp:
    """ ServerApp """

    __log = get_logger(__name__, False)

    def __init__(self, port, debug=False):
        """ init """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('port=%s', port)

        self._port = port

    def main(self):
        """ main """
        self.__log.debug('')

    def end(self):
        """ end """
        self.__log.debug('')


@click.command(help="TCP Command Server")
@click.option('--port', '-p', 'port', type=int, default=Server.DEF_PORT,
              htlp='port number (default: %s)' % (Server.DEF_PORT))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
@click.pass_obj
def server(obj, port, debug):
    """ Server """
    debug = obj['debug'] or debug
    __log = get_logger(__name__, debug)
    __log.debug('obj=%s, port=%s', obj, port)

    obj = ServerApp(port, debug=debug)
    try:
        obj.main()
    finally:
        obj.end()
