import json
import websocket
from mcdreforged.api.all import *
from mcdreforged.api.rcon import RconConnection

config = {
    'command_prefix': '!!wl',
    'servers': [
        {
            'server_name': 'Creative',
            'rcon_address': '127.0.0.1',
            'rcon_port': 25575,
            'rcon_password': 'PASSWORD'
        },
        {
            'server_name': 'Mirror',
            'rcon_address': '127.0.0.1',
            'rcon_port': 25576,
            'rcon_password': 'PASSWORD'
        },
        {
            'server_name': 's',
            'rcon_address': '127.0.0.1',
            'rcon_port': 25570,
            'rcon_password': 'PASSWORD'
        }
    ],
    'convert_vanilla_whitelist': False,
    'convert_lls_whitelist': False,
    'ws_address': '127.0.0.1',
    'ws_port': 6700,
    'access_token': 'ACCESSTOKEN',
    'group_id': 000
}
default_config = config.copy()

whitelist = {
    "uuid": {
        "name": "tangsu",
        "qq": "100001",
        "whitelist": False
    }
}


class websocket(websocket.WebSocketApp):
    ...


def wlfl():
    wlf = open('./config/qq_whitelist/whitelist.json', 'r')
    try:
        wlf = json.loads(wlf.read())
    except:
        return json.loads(str({}))
    else:
        return wlf


def help_messag(src: CommandSource):
    src.reply('''{0} add <player> <qq_id>:添加白名单。
{0} remove player <player>:通过玩家ID移除白名单。
{0} remove qq <player>:通过玩家绑定的qq账号移除白名单。
{0} list:查看白名单列表。'''.format(config.get('command_prefix')))


def open_whitelist(whitelist_file):
    data = open(whitelist_file, "r")
    data = json.loads(data.read())
    return data


def get_uuid(server: PluginServerInterface, player):
    api = server.get_plugin_instance('mc_uuid')
    return api.onlineUUID(player)


def write_wl(server: PluginServerInterface, player, qq):
    player_uuid = str(get_uuid(server, player))
    uuid = player_uuid
    player_uuid = {
        'name': player,
        'qq': qq,
        'whitelist': True
    }
    whitelist.get(uuid)
    whitelist[uuid] = player_uuid
    data = json.dumps(whitelist)
    wlf = open('./config/qq_whitelist/whitelist.json', 'w')
    wlf.write(data)
    wlf.close()


def convert_vanilla_whitelist(ctx):
    whitelist = open_whitelist("./server/whitelist.json")
    for i in whitelist:
        print(i['name'])


def convert_lls_whitelist(ctx):
    whitelist = open_whitelist("./config/qq_whitelist/whitelist.json")
    # print(whitelist)


def rcon_reload_command(server: ServerInterface, src):
    rcon_server = config['servers']
    src.reply('[DEBUG] {0}'.format(rcon_server))

    for i in rcon_server:
        address = i['rcon_address']
        port = i['rcon_port']
        password = i['rcon_password']
        server_name = i['server_name']
        rcon = RconConnection(address, port, password)
        try:
            t = rcon.connect()
        except:
            src.reply('{0} 无法连接,请检查 config'.format(server_name))
        if t:
            reply = rcon.send_command('whitelist reload')
            src.reply('{0} 已同步\n{0}:{1}'.format(server_name, reply))
            rcon.disconnect()


def wlist():
    wlist = []
    for i in whitelist:
        wlist.append(whitelist[i]['name'])
    return wlist


class Command:
    def __init__(self, src: CommandSource, server: PluginServerInterface):
        self.src = src
        self.server = server

    def whitelist_add(self, ctx):
        write_wl(self.server, ctx['player_name'], ctx['qq'])
        self.src.reply('白名单内玩家：'+ wlist())

    def whitelist_remove_player(self, ctx):
        self.src.reply(ctx)

    def whitelist_remove_qq(self, ctx):
        self.src.reply(ctx)

    def whitelist_list(self, whitelist):
        # self.src.reply()
        self.src.reply(wlist())

    def sync_whitelist(self):
        rcon_reload_command(self.server, self.src)


def on_load(server: PluginServerInterface, prev_module):
    global config
    config = server.load_config_simple('config.json', default_config)

    global whitelist
    whitelist = wlfl()

    server.register_command(
        Literal(config['command_prefix']).runs(lambda src: help_messag(src)).
            then(
            Literal('add').
                then(
                Text('player_name').
                    then(
                    Text('qq').runs(lambda src, ctx: Command(src, server).whitelist_add(ctx))
                )
            )

        ).
            then(
            Literal('remove').
                then(
                Literal('player').
                    then(
                    Text('player_name').
                        runs(lambda src, ctx: Command(src, server).whitelist_remove_player(ctx))
                )
            ).
                then(
                Literal('qq').
                    then(
                    Integer('qq').
                        runs(lambda src, ctx: Command(src, server).whitelist_remove_qq(ctx))
                )
            )
        ).
            then(
            Literal('list').
                runs(lambda src: Command(src, server).whitelist_list(whitelist))
        ).
            then(
            Literal('sync').
                runs(lambda src: Command(src, server).sync_whitelist())
        ).
            then(
            Literal('wlc').
                then(
                Literal('vanilla').
                    runs(lambda ctx: convert_vanilla_whitelist(ctx))
            ).
                then(
                Literal('lls').
                    runs(lambda ctx: convert_lls_whitelist(ctx))
            )
        )
    )


def on_unload(server: PluginServerInterface):
    ...
