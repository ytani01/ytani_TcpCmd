#
# Copyright (c) 2021 Yoichi Tanibayashi
#
import click
from .my_logger import get_logger


class Server:
    """ Server """

    __log = get_logger(__name__, False)

    def __init__(self, debug=False):
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)

    def server(self, arg1):
        """ method1 """
        self.__log.debug('arg=%s', arg1)

        print('Hello, %s' % (arg1))


@click.command(help="Server")
@click.argument('arg1', type=str)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
@click.pass_obj
def server(obj, arg1, debug):
    """ Server """
    debug = obj['debug'] or debug

    __log = get_logger(__name__, debug)
    __log.debug('obj=%s, arg1=%s', obj, arg1)

    cmd_obj = Server(debug=debug)
    cmd_obj.server(arg1)
