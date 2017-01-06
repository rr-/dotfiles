# adapted from python-mpd.
# - fixed py3.6 compatibility
# - fixed sending boolean arguments ('random 1', 'random 0')
# - used assertions over exceptions
# - other visual refactors
# - removed unused features such as command lists and lazy iteration guards

import socket


HELLO_PREFIX = 'OK MPD '
ERROR_PREFIX = 'ACK '
SUCCESS = 'OK'
NEXT = 'list_OK'


class MpdError(Exception):
    pass


class ConnectionError(MpdError):
    pass


class CommandError(MpdError):
    pass


class _NotConnected:
    def __getattr__(self, attr):
        return self._dummy

    def _dummy(self, *_args):
        raise ConnectionError('Not connected')


def escape(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')


class MpdClient:
    def __init__(self):
        self.mpd_version = None
        self._pending = []
        self._sock = None
        self._rfile = _NotConnected()
        self._wfile = _NotConnected()

        self._commands = {
            # Status Commands
            'clearerror':         self._fetch_nothing,
            'currentsong':        self._fetch_object,
            'idle':               self._fetch_list,
            'noidle':             None,
            'status':             self._fetch_object,
            'stats':              self._fetch_object,
            # Playback Option Commands
            'consume':            self._fetch_nothing,
            'crossfade':          self._fetch_nothing,
            'mixrampdb':          self._fetch_nothing,
            'mixrampdelay':       self._fetch_nothing,
            'random':             self._fetch_nothing,
            'repeat':             self._fetch_nothing,
            'setvol':             self._fetch_nothing,
            'single':             self._fetch_nothing,
            'replay_gain_mode':   self._fetch_nothing,
            'replay_gain_status': self._fetch_item,
            'volume':             self._fetch_nothing,
            # Playback Control Commands
            'next':               self._fetch_nothing,
            'pause':              self._fetch_nothing,
            'play':               self._fetch_nothing,
            'playid':             self._fetch_nothing,
            'previous':           self._fetch_nothing,
            'seek':               self._fetch_nothing,
            'seekid':             self._fetch_nothing,
            'stop':               self._fetch_nothing,
            # Playlist Commands
            'add':                self._fetch_nothing,
            'addid':              self._fetch_item,
            'clear':              self._fetch_nothing,
            'delete':             self._fetch_nothing,
            'deleteid':           self._fetch_nothing,
            'move':               self._fetch_nothing,
            'moveid':             self._fetch_nothing,
            'playlist':           self._fetch_playlist,
            'playlistfind':       self._fetch_songs,
            'playlistid':         self._fetch_songs,
            'playlistinfo':       self._fetch_songs,
            'playlistsearch':     self._fetch_songs,
            'plchanges':          self._fetch_songs,
            'plchangesposid':     self._fetch_changes,
            'shuffle':            self._fetch_nothing,
            'swap':               self._fetch_nothing,
            'swapid':             self._fetch_nothing,
            # Stored Playlist Commands
            'listplaylist':       self._fetch_list,
            'listplaylistinfo':   self._fetch_songs,
            'listplaylists':      self._fetch_playlists,
            'load':               self._fetch_nothing,
            'playlistadd':        self._fetch_nothing,
            'playlistclear':      self._fetch_nothing,
            'playlistdelete':     self._fetch_nothing,
            'playlistmove':       self._fetch_nothing,
            'rename':             self._fetch_nothing,
            'rm':                 self._fetch_nothing,
            'save':               self._fetch_nothing,
            # Database Commands
            'count':              self._fetch_object,
            'find':               self._fetch_songs,
            'findadd':            self._fetch_nothing,
            'list':               self._fetch_list,
            'listall':            self._fetch_database,
            'listallinfo':        self._fetch_database,
            'lsinfo':             self._fetch_database,
            'search':             self._fetch_songs,
            'update':             self._fetch_item,
            'rescan':             self._fetch_item,
            # Sticker Commands
            'sticker get':        self._fetch_item,
            'sticker set':        self._fetch_nothing,
            'sticker delete':     self._fetch_nothing,
            'sticker list':       self._fetch_list,
            'sticker find':       self._fetch_songs,
            # Connection Commands
            'close':              None,
            'kill':               None,
            'password':           self._fetch_nothing,
            'ping':               self._fetch_nothing,
            # Audio Output Commands
            'disableoutput':      self._fetch_nothing,
            'enableoutput':       self._fetch_nothing,
            'outputs':            self._fetch_outputs,
            # Reflection Commands
            'commands':           self._fetch_list,
            'notcommands':        self._fetch_list,
            'tagtypes':           self._fetch_list,
            'urlhandlers':        self._fetch_list,
            'decoders':           self._fetch_plugins,
        }

    @property
    def connected(self):
        return self._sock is not None

    def connect(self, host, port):
        if self.connected:
            raise ConnectionError('Already connected')

        for res in socket.getaddrinfo(
                host, port, socket.AF_UNSPEC,
                socket.SOCK_STREAM, socket.IPPROTO_TCP,
                socket.AI_ADDRCONFIG):
            # pylint: disable=invalid-name
            af, socktype, proto, _canonname, sa = res
            try:
                self._sock = socket.socket(af, socktype, proto)
                self._sock.connect(sa)
                break
            except socket.error:
                if self._sock:
                    self._sock.close()
                    self._sock = None
        else:
            raise ConnectionError('Unable to connect')

        self._rfile = self._sock.makefile('r')
        self._wfile = self._sock.makefile('w')
        try:
            self._hello()
        except:
            self.disconnect()
            raise

    def disconnect(self):
        self._rfile.close()
        self._wfile.close()
        self._sock.close()
        self.mpd_version = None
        self._pending = []
        self._sock = None
        self._rfile = _NotConnected()
        self._wfile = _NotConnected()

    def __getattr__(self, attr):
        if attr.startswith('send_'):
            command = attr.replace('send_', '', 1)
            wrapper = self._send
        elif attr.startswith('fetch_'):
            command = attr.replace('fetch_', '', 1)
            wrapper = self._fetch
        else:
            command = attr
            wrapper = self._execute
        if command not in self._commands:
            command = command.replace('_', ' ')
            assert command in self._commands
        return lambda *args: wrapper(command, args)

    def _send(self, command, args):
        self._write_command(command, args)
        retval = self._commands[command]
        if retval is not None:
            self._pending.append(command)

    def _fetch(self, command, _args=None):
        assert self._pending
        assert self._pending[0] == command
        del self._pending[0]
        retval = self._commands[command]
        if callable(retval):
            return retval()
        return retval

    def _execute(self, command, args):
        assert not self._pending
        retval = self._commands[command]
        self._write_command(command, args)
        if callable(retval):
            return retval()
        return retval

    def _write_line(self, line):
        self._wfile.write('%s\n' % line)
        self._wfile.flush()

    def _write_command(self, command, args=None):
        parts = [command]
        if args:
            for arg in args:
                if arg is True or arg is False:
                    parts.append(str(int(arg)))
                else:
                    parts.append("'%s'" % escape(str(arg)))
        self._write_line(' '.join(parts))

    def _read_line(self):
        line = self._rfile.readline()
        assert line.endswith('\n')
        line = line.rstrip('\n')
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            raise CommandError(error)
        if line == SUCCESS:
            return
        return line

    def _read_pair(self, separator):
        line = self._read_line()
        if line is None:
            return
        pair = line.split(separator, 1)
        assert len(pair) >= 2
        return pair

    def _read_pairs(self, separator=': '):
        pair = self._read_pair(separator)
        while pair:
            yield pair
            pair = self._read_pair(separator)

    def _read_list(self):
        seen = None
        for key, value in self._read_pairs():
            assert seen is None or key == seen
            seen = key
            yield value

    def _read_playlist(self):
        for _key, value in self._read_pairs(':'):
            yield value

    def _read_objects(self, delimiters=None):
        obj = {}
        for key, value in self._read_pairs():
            key = key.lower()
            if delimiters and key in delimiters:
                yield obj
                obj = {}

            if key in obj:
                if isinstance(obj[key], list):
                    obj[key].append(value)
                else:
                    obj[key] = [obj[key], value]
            else:
                obj[key] = value
        if obj:
            yield obj

    def _fetch_nothing(self):
        line = self._read_line()
        assert line is None

    def _fetch_item(self):
        pairs = list(self._read_pairs())
        if len(pairs) != 1:
            return
        return pairs[0][1]

    def _fetch_list(self):
        return self._read_list()

    def _fetch_playlist(self):
        return self._read_playlist()

    def _fetch_object(self):
        objs = list(self._read_objects())
        if not objs:
            return {}
        return objs[0]

    def _fetch_objects(self, delimiters):
        return list(self._read_objects(delimiters))

    def _fetch_changes(self):
        return self._fetch_objects(['cpos'])

    def _fetch_songs(self):
        return self._fetch_objects(['file'])

    def _fetch_playlists(self):
        return self._fetch_objects(['playlist'])

    def _fetch_database(self):
        return self._fetch_objects(['file', 'directory', 'playlist'])

    def _fetch_outputs(self):
        return self._fetch_objects(['outputid'])

    def _fetch_plugins(self):
        return self._fetch_objects(['plugin'])

    def _hello(self):
        line = self._rfile.readline().rstrip('\n')
        assert line.startswith(HELLO_PREFIX)
        self.mpd_version = line[len(HELLO_PREFIX):].strip()
