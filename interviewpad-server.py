import os
from contextlib import contextmanager

from past.builtins import basestring # python2/3 `pip install future`
from configparser import RawConfigParser
from functools import wraps, partial
import subprocess
import click
import sys

from click import BaseCommand, Command

from flask_interviewpad.constants import config_exists, get_config, CONFIG_PATH, save_config


# def require_config(fn,extra=None):
#     if not callable(fn):
#         return partial(require_config,extra=fn)
#
#     def __inner(*args,**kwargs):
#         print("CHECK:?",extra,sys.argv)
#         if not config_exists():
#             click.echo("WARNING NO CONFIG FILE FOUND!!!", err=True)
#             result = click.prompt("WOULD YOU LIKE TO SETUP CONFIG NOW(y/n)?", type=click.Choice(['y', 'n']))
#             if result == "n":
#                 click.echo("GOODBYE! you cannot continue without configuring the system", err=True)
#                 sys.exit(1)
#             old_argv = sys.argv[:]
#             try:
#                 sys.argv.pop(1)
#                 return runsetup()
#             finally:
#                 sys.argv[:] = old_argv
#         if extra:
#             print("Got Extra!",extra)
#             a_list = extra
#             if isinstance(a_list, basestring):
#                 a_list =[a_list,]
#             assert isinstance(a_list,(list,tuple))
#             for ext in extra:
#                 print("EXTRA:",ext)
#
#
#         return fn(*args,**kwargs)
#     if hasattr(fn,'parse_args'):
#         fn.parse_args = lambda a,b,y=fn:__inner(y.parse_args)
#         return fn
#     return __inner
@click.group()
def cli():
    pass
def run_cmd(cmd,stdout=sys.stdout,stderr=sys.stderr):
    print("CALL:",[sys.executable, sys.argv[0], cmd.name])
    return subprocess.Popen([sys.executable, sys.argv[0], cmd.name], stderr=stderr,
                     stdout=stdout)

class CfgReq(Command):
    def __init__(self,*args,**kwargs):
        self.require = kwargs.pop("require",[])
        if isinstance(self.require,basestring):
            self.require = [self.require,]
        assert isinstance(self.require,(list,tuple))
        Command.__init__(self,*args,**kwargs)
    def get_params(self, ctx):
        print( "???")
        if not config_exists():
            click.echo("WARNING NO CONFIG FILE FOUND!!!", err=True)
            result = click.prompt("WOULD YOU LIKE TO SETUP CONFIG NOW(y/n)?", type=click.Choice(['y', 'n']))
            if result == "n":
                click.echo("GOODBYE! you cannot continue without configuring the system", err=True)
                sys.exit(1)
            subprocess.Popen([sys.executable, sys.argv[0],'runsetup'], stderr=sys.stderr,
                             stdout=sys.stdout).communicate()


        if self.require:
            cfg = get_config()
            for item in self.require:
                print("CHK:", item, cfg.has_section(item))
                if not cfg.has_section(item):
                    cmd = globals().get('setup_'+item,None)
                    if cmd:
                       click.echo("It appears your {0} is not setup".format(item))
                       result = click.prompt("WOULD YOU LIKE TO SETUP {0} NOW(y/n)?".format(item),
                                             type=click.Choice(['y', 'n']))
                       if result == "n":
                           click.echo("GOODBYE! you cannot continue without configuring the system", err=True)
                           sys.exit(1)
                       print("SETUP {0} NOW".format(item))
                       subprocess.Popen([sys.executable,sys.argv[0],cmd.name],stderr=sys.stderr,stdout=sys.stdout).communicate()
                    else:
                        raise Exception("Cannot find setup_{0} method".format(item))


        return Command.get_params(self, ctx)

@click.command(cls=CfgReq,
               help="add a new user to the site, this requires a database to be setup!",
               require=["db",])
@click.option("--nickname",prompt=True)
@click.option("--realname",prompt=True)
@click.option("--email",prompt=True)
@click.option("--pw",prompt='Enter Password')
def adduser(nickname,realname,email,pw):
    cfg = get_config()
    if not cfg.has_section('db') or not cfg.get('db','uri'):
        click.echo("WARNING Database Is Not Configured!!!", err=True)
        result = click.prompt("Configure Database Now(y/n)?", type=click.Choice(['y', 'n']))
        if result == "n":
            click.echo("GOODBYE! you cannot add a user without configuring the database", err=True)
            sys.exit(1)
        run_cmd(setup_db)
    click.echo('Add User:{0} {1} {2}'.format(nickname,realname,email))
    with db_context(cfg.get('db','uri')) as db:
        from flask_interviewpad.models import User
        user = User(nickname=nickname,email=email,realname=realname)
        db.session.add(user)
        db.session.commit()
        click.echo("Created User: {0}".format(user))



@contextmanager
def db_context(db_uri):
    from flask import Flask
    from flask_interviewpad.models import init_app,db
    a = Flask("__main__")
    init_app(a)
    yield db
    del a



@click.command(help="configure the database uri, see http://flask-sqlalchemy.pocoo.org/2.3/config/#connection-uri-format")
@click.option('--uri',prompt="Database URI(<type>://[user]:[password]@<host>/<db>)",help="http://flask-sqlalchemy.pocoo.org/2.3/config/#connection-uri-format")
def setup_db(uri):
    config = get_config()
    if(not config.has_section('db')):
        config.add_section('db')
    config.set("db","uri",uri)
    save_config(config)
    with db_context(uri) as db:
        db.create_all()
    print("DATABASE CONFIGURED AND CREATED!")

@click.command(help="configure the email server")
@click.option('--smtp-server',prompt="SMTP Server(and port)",help="the server and port of the smtp server (ie smtp.gmail.com:465)")
@click.option('--user',prompt="SMTP Username",help="the username (ie username@gmail.com)")
@click.option('--pw',prompt="SMTP Password",help="the password (ie myS3cretP4ss)")
def setup_smtp(smtp_server,user,pw):
    config = get_config()
    if (not config.has_section('smtp')):
        config.add_section('smtp')
    config.set("smtp", "server", smtp_server)
    config.set("smtp", "user", user)
    config.set("smtp", "pw", pw)
    save_config(config)


@click.command(help="setup the whole site!")
@click.option("--skip-db",is_flag=True,default=False)
@click.option("--skip-smtp",is_flag=True,default=False)
@click.option("--skip-adduser",is_flag=True,default=False)
def runsetup(skip_db,skip_smtp,skip_adduser):
    if not config_exists():
        RawConfigParser().write(open(CONFIG_PATH,"wb"))
    click.echo("SETUP DATABASE")
    run_cmd(setup_db).communicate()
    click.echo("SETUP Email Service")
    run_cmd(setup_smtp).communicate()


@click.command(help="run a server here")
@click.option('--host', default='127.0.0.1', help='the host interface to serve on.')
@click.option('--port', default='8080',help='The port to serve on')
def serve(host,port):
    if not config_exists():
        click.echo("WARNING NO CONFIG FILE FOUND!!!",err=True)
        result = click.prompt("WOULD YOU LIKE TO SETUP CONFIG NOW(y/n)?",type=click.Choice(['y', 'n']))
        if result == "n":
            click.echo("GOODBYE! you cannot continue without configuring the system", err=True)
            sys.exit(1)

    click.echo("Serving on {host}:{port}".format(host=host,port=port))

cli.add_command(runsetup)
cli.add_command(setup_db)
cli.add_command(setup_smtp)
cli.add_command(adduser)
cli.add_command(serve)

if __name__ == '__main__':
    cli()