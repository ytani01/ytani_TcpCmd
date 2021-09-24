#
# Copyright (c) 2021 Yoichi Tanibayashi
#
import socketserver
import sys
import threading
import queue
import time
import click
from .my_logger import get_logger


class Worker(threading.Thread):
    """ Worker """

    __log = get_logger(__name__, False)

    DEF_RECV_TIMEOUT = 0.2  # sec

    def __init__(self, svr, debug=False):
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('')

        self._svr = svr

        self._cmdq = queue.Queue()
        self._active = False

        super().__init__(daemon=True)

    def __del__(self):
        """ __del__ """
        self._active = False
        self.__log.debug('')

    def end(self):
        """ end """
        self.__log.debug('')
        self._active = False
        self.join()
        self.__log.debug('done')

    def send(self, cmd):
        """ send """
        self.__log.debug('cmd=%a', cmd)

        self._cmdq.put(cmd)

    def recv(self, timeout=DEF_RECV_TIMEOUT):
        """ recv """
        # self.__log.debug('timeout=%.1f', timeout)

        try:
            cmd = self._cmdq.get(timeout=timeout)
        except queue.Empty:
            cmd = ''
        else:
            self.__log.debug('cmd=%a', cmd)

        return cmd

    def run(self):
        """ run """

        self._active = True
        while self._active:
            cmd = self.recv()

            if cmd == '':
                time.sleep(0.1)
                continue

            self.__log.debug('cmd=%a', cmd)

            time.sleep(3)

        self.__log.debug('done')


class Handler(socketserver.StreamRequestHandler):
    """ Handler """

    __log = get_logger(__name__, False)

    def __init__(self, request, client_address, svr):
        """ init """
        self._dbg = svr._dbg
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('client_address: %s', client_address)

        self._svr = svr
        self._worker = self._svr._worker

        return super().__init__(request, client_address, svr)

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
        except BrokenPipeError as ex:
            self.__log.debug('%s:%s', type(ex).__name__, ex)
        except Exception as ex:
            self.__log.warning('%s:%s', type(ex).__name__, ex)

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

        while self._svr._active:
            # データー受信
            try:
                self.__log.debug('recv..')
                net_data = self.request.recv(512)
            except ConnectionResetError as ex:
                self.__log.warning('%s:%s.', type(ex), ex)
                return
            except BaseException as ex:
                self.__log.warning('BaseException:%s:%s.', type(ex), ex)
                # TBD
                break
            except Exception as ex:
                self.__log.warning('Exception:%s:%s.', type(ex), ex)
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

            # self.net_write('\r\n'.encode('utf-8'))

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

            self._worker.send(data)

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

        self._worker = Worker(svr=self, debug=self._dbg)
        self._active = False

        self.allow_reuse_address = True  # Important !!

        try:
            super().__init__(('', self._port), Handler)
        except Exception as ex:
            self.__log.warning('%s:%s', type(ex).__name__, ex)
            sys.exit()
            # return None

    def serve_forever(self, poll_interval=0.5):
        """  serve_forever """
        self.__log.debug('')
        self._active = True
        self._worker.start()
        return super().serve_forever(poll_interval)

    def end(self):
        """ end """
        self.__log.debug('')

        self._active = False
        self.shutdown()
        if self._worker._active:
            self._worker.end()

        self.__log.debug('done')

        # TBD
        # 接続中の Handler を強制終了するためにこのようにしているが、
        # もっといい方法がないのか?
        raise KeyboardInterrupt  # TBD ??

    def __del__(self):
        self.__log.debug('')
        self._active = False
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
