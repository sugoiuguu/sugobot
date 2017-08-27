import hooks as hk

from irc import *
from util import *
from sys import argv, stdout

config_path = 'config.json'

# logger
class IRC_Log:
    def __init__(self, path):
        self.path = path

    def write(self, msg):
        with open(self.path, 'a') as log:
            log.write(msg)
            log.close()

# reload all the bot hooks and config
def reload_hook(irc_con):
    if irc_con.msg_matches[0] == irc_con.cmd('reload'):
        target = irc_con.matches[2]
        host = irc_con.matches[0]

        if target[0] != '#':
            target = parse_nick(host)

        if host not in irc_con.extern['admin_hosts']:
            irc_con.privmsg(target, irc_con.extern['msg_error'])
        else:
            try:
                reload(hk)
                irc_con.reset_hooks(hk.exports)
                irc_con.install_hook('PRIVMSG', 'reload', reload_hook)
                irc_con.load_config(config_path)
                irc_con.privmsg(target, 'successfully reloaded bot config and hooks')
            except IOError:
                irc_con.privmsg(target, 'error reloading config')

# main procedure
if __name__ == '__main__':
    log = None

    try:
        log = IRC_Log(argv[1])
    except IndexError:
        log = stdout

    irc = IRC_Conn(config_path, hk.exports, log)
    irc.install_hook('PRIVMSG', 'reload', reload_hook)

    irc.connect_to_server()
    irc.auth()
    irc.join_configured_channels() # FIXME: this shit isn't working in some servers,
                                   # you need to manually join the channels

    while True:
        try:
            irc.logger.write(irc.recv())
            irc.trigger_hooks()
        except IRC_Conn.exceptions['exit']:
            break
