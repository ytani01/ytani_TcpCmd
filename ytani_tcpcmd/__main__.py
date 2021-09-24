#
# Copyright (c) 2021 Yoichi Tanibayashi
#
import click
from . import server, client
from . import __prog_name__, __version__, __author__
from .my_logger import get_logger


@click.group(invoke_without_command=True,
             context_settings=dict(help_option_names=['-h', '--help']),
             help=" by " + __author__)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, debug):
    """ command group """
    __log = get_logger(__name__, debug)

    ctx.obj = {'debug': debug}

    subcmd = ctx.invoked_subcommand
    __log.debug('subcmd=%s', subcmd)

    if not subcmd:
        print(ctx.get_help())


cli.add_command(server)
cli.add_command(client)

if __name__ == '__main__':
    cli(prog_name=__prog_name__)
