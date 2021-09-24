#
# Copyright (c) 2021 Yoichi Tanibayashi
#
import click
import time
import telnetlib
from .server import Server
from .my_logger import get_logger


class Client:
    """ Client """

    __log = get_logger(__name__, False)

    def __init__(self, svr_host, svr_port, debug=False):
        """ init """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('(svr_host, svr_port) = %s', (svr_host, svr_port))

        self._svr_host = svr_host
        self._svr_port = svr_port

        self._tn = telnetlib.Telnet(self._svr_host, self._svr_port)

    def end(self):
        """ end """
        self.__log.debug('')
        self.close()

    def close(self):
        """ close """
        self.__log.debug('')
        self._tn.close()

    def send(self, arg_str):
        """ send """
        self.__log.debug('arg_str=%a', arg_str)

        ret = '_'
        opening = ''
        while len(ret) > 0:
            ret = self.recv()
            opening += ret

        self.__log.debug('opening=%a', opening)

        try:
            self._tn.write(arg_str.encode('utf-8'))
            self.__log.debug('sent: %a', arg_str)
        except Exception as ex:
            self.__log.warning('%s:%s', type(ex).__name__, ex)

        return opening

    def recv(self):
        """ recv """
        self.__log.debug('')

        buf = b''
        while True:
            time.sleep(0.1)
            try:
                in_data = self._tn.read_eager()
            except Exception as ex:
                self.__log.warning('%s:%s', type(ex).__name__, ex)
                in_data = b''

            if len(in_data) == 0:
                break

            self.__log.debug('in_data=%a', in_data)
            buf += in_data

        self.__log.debug('buf=%a', buf)
        try:
            ret_str = buf.decode('utf-8')
        except UnicodeDecodeError:
            if buf == b'':
                ret_str = ''
            else:
                ret_str = str(buf)

        self.__log.debug('ret_str=%a', ret_str)

        return ret_str


class ClientApp:
    """ Client """

    __log = get_logger(__name__, False)

    def __init__(self, svr_host="localhost", svr_port=Server.DEF_PORT,
                 arg_str="", debug=False):
        """ __init__ """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('(svr_host, svr_port)=%s', (svr_host, svr_port))
        self.__log.debug('arg_str=%a', arg_str)

        self._arg_str = arg_str
        self._svr_host = svr_host
        self._svr_port = svr_port

        self._cl_obj = Client(self._svr_host, self._svr_port, debug=self._dbg)

    def main(self):
        """ main """
        self.__log.debug('')
        opening = self._cl_obj.send(self._arg_str)
        print('opening=%a' % opening)

        # time.sleep(10)

        reply = self._cl_obj.recv()
        print('reply=%a' % reply)

    def end(self):
        """ end """
        self.__log.debug('')
        self._cl_obj.end()


@click.command(help="Client")
@click.argument('arg', type=str, nargs=-1)
@click.option('--svr_host', '-s', 'svr_host', type=str, default="localhost",
              help='server host name (default: localhost)')
@click.option('--svr_port', '-p', 'svr_port', type=int,
              default=Server.DEF_PORT,
              help='server port number (default: %s)' % (Server.DEF_PORT))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
@click.pass_obj
def client(obj, arg, svr_host, svr_port, debug):
    """ Client """
    debug = obj['debug'] or debug
    __log = get_logger(__name__, debug)
    __log.debug('obj=%s, arg=%s, svr_host=%s, svr_port=%s',
                obj, arg, svr_host, svr_port)

    arg_str = ' '.join(arg)

    obj = ClientApp(svr_host, svr_port, arg_str, debug=debug)
    try:
        obj.main()
    finally:
        obj.end()
