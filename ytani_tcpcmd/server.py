#
# Copyright (c) 2021 Yoichi Tanibayashi
#
import socketserver
import sys
import socket
import threading
import queue
import json
import time
import click
from .my_logger import get_logger


class Handler(socketserver.StreamRequestHandler):
    """ Handler """

    __log = get_logger(__name__, False)

    def __init__(self, request, client_address, server):
        """ init """
        self._dbg = server._dbg
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('client_address: %s', client_address)

        self._svr = server

        return super().__init__(request, client_address, server)

    def setup(self):
        """ setup """
        self.__log.debug('')
        return super().setup()

    def finish(self):
        self.__log.debug('')
        return super().finish()

    def net_write(self, msg):
        """ net_write """
        self.__log.debug('msg=%a', msg)

        try:
            self.wfile.write(msg)
        except BrokenPipeError as e:
            self.__log.debug('%s:%s', type(e).__name__, e)
        except Exception as e:
            self.__log.warning('%s:%s', type(e).__name__, e)

    def handle(self):
        """ handle """
        self.__log.debug('')

        # Telnet Protocol
        #
        # mode character
        #  0xff IAC
        #  0xfd D0
        #  0x22 LINEMODE
        # self.net_write(b'\xff\xfd\x22')

        self.net_write('# Ready\r\n'.encode('utf-8'))

        net_data = b''
        flag_continue = True
        while flag_continue:
            # データー受信
            try:
                net_data = self.request.recv(512)
            except ConnectionResetError as ex:
                self.__log.warning('%s:%s.', type(ex), ex)
                return
            except BaseException as ex:
                self.__log.warning('BaseException:%s:%s.', type(ex), ex)
                # TBD
                break
            else:
                self.__log.debug('net_data:%a', net_data)

            # デコード(UTF-8)
            try:
                decoded_data = net_data.decode('utf-8')
            except UnicodeDecodeError as ex:
                self.__log.warning('%s:%s .. ignored', type(ex), ex)
                continue
            else:
                self.__log.debug('decoded_data:%a', decoded_data)

            self.net_write('\r\n'.encode('utf-8'))

            # 文字列抽出(コントロールキャラクター削除)
            data = ''
            for ch in decoded_data:
                if ord(ch) >= 0x20:
                    data += ch
            self.__log.debug('data=%a', data)

            # 文字数が0の場合、コネクションが切断されたと判断し終了
            if len(data) == 0:
                msg = '# No data .. disconnect'
                self.__log.warning(msg)
                self.net_write((msg + '\r\n').encode('utf-8'))
                break

        self.__log.debug('done')


class Server(socketserver.ThreadingTCPServer):
    """ Server """

    __log = get_logger(__name__, False)

    DEF_PORT = 12345

    def __init__(self, port=DEF_PORT, debug=False):
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('port=%s', port)

        self._port = port

        try:
            super().__init__(('', self._port), Handler)
        except Exception as ex:
            self.__log.warning('%s:%s', type(ex).__name__, ex)
            sys.exit()
            # return None

    def serve_forever(self):
        """  serve_forever """
        self.__log.debug('')
        return super().serve_forever()

    def end(self):
        """ end """
        self.__log.debug('')

        self.__log.debug('done')

    def _del_(self):
        self.__log.debug('')
        self.end()


class ServerApp:
    """ ServerApp """

    __log = get_logger(__name__, False)

    def __init__(self, port, debug=False):
        """ init """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('port=%s', port)

        self._port = port
        self._svr = Server(self._port, debug=self._dbg)

    def main(self):
        """ main """
        self.__log.debug('start server')
        self._svr.serve_forever()

    def end(self):
        """ end """
        self.__log.debug('')
        self._svr.end()
        self.__log.debug('done')


@click.command(help="TCP Command Server")
@click.option('--port', '-p', 'port', type=int, default=Server.DEF_PORT,
              help='port number (default: %s)' % (Server.DEF_PORT))
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
