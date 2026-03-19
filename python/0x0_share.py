# -*- coding: utf-8 -*-
"""
0x0 Share plugin compatible with HexChat / ZoiteChat.

- Right-click tab menu entry: Share File via 0x0...
- Main menu entries: Share File, Preferences, Reset Host
- Configurable 0x0-compatible endpoint stored in plugin preferences
- Uploads selected file to configured 0x0-style instance
- Sends returned URL into the tab where the action was started
"""

from __future__ import absolute_import, print_function

import mimetypes
import os
import queue
import ssl
import threading
import uuid

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

import hexchat

__module_name__ = "0x0 Share"
__module_version__ = "0.1.0"
__module_description__ = "Upload a file to a 0x0.st-compatible host and paste the returned URL into chat"

DEFAULT_ENDPOINT = "https://0x0.st"
USER_AGENT = "zoitechat-0x0-share/0.1.0"
PREF_KEY_ENDPOINT = "x0share_endpoint"
RESULTS = queue.Queue()

GTK_AVAILABLE = False
TK_AVAILABLE = False
Gtk = None

try:
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    GTK_AVAILABLE = True
except Exception:
    Gtk = None

if not GTK_AVAILABLE:
    try:
        import tkinter as tk
        from tkinter import filedialog, simpledialog

        TK_AVAILABLE = True
    except Exception:
        tk = None
        filedialog = None
        simpledialog = None

MENU_PATHS = [
    '$TAB/0x0 Share',
    '$TAB/0x0 Share/Share File...',
    '$TAB/0x0 Share/Preferences...',
    '$TAB/0x0 Share/Reset Host to Default',
    '$CHAN/0x0 Share',
    '$CHAN/0x0 Share/Share File...',
    '$CHAN/0x0 Share/Preferences...',
    '$CHAN/0x0 Share/Reset Host to Default',
]

def _quote_for_menu(value):
    return '"{}"'.format(value.replace('\\', '\\\\').replace('"', '\\"'))



def _plugin_print(message):
    hexchat.prnt('[0x0-share] {}'.format(message))



def _normalize_endpoint(raw_value):
    value = (raw_value or '').strip()
    if not value:
        value = DEFAULT_ENDPOINT

    if not value.startswith('http://') and not value.startswith('https://'):
        value = 'https://{}'.format(value)

    parsed = urlparse(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError('Invalid upload host: {}'.format(raw_value))

    normalized = value.rstrip('/')
    return normalized or DEFAULT_ENDPOINT



def _get_endpoint():
    stored = hexchat.get_pluginpref(PREF_KEY_ENDPOINT)
    if not stored:
        return DEFAULT_ENDPOINT

    try:
        return _normalize_endpoint(stored)
    except ValueError:
        return DEFAULT_ENDPOINT



def _set_endpoint(value):
    endpoint = _normalize_endpoint(value)
    if not hexchat.set_pluginpref(PREF_KEY_ENDPOINT, endpoint):
        raise RuntimeError('Failed to save plugin preference.')
    return endpoint



def _reset_endpoint():
    try:
        hexchat.del_pluginpref(PREF_KEY_ENDPOINT)
    except Exception:
        # Older/plugin-specific oddities are non-fatal here.
        pass



def _current_context_requires_target(ctx):
    if ctx is None:
        return False

    channel = ctx.get_info('channel')
    return bool(channel)



def _menu_add(path, command=None):
    if command:
        hexchat.command('MENU ADD {} {}'.format(_quote_for_menu(path), _quote_for_menu(command)))
    else:
        hexchat.command('MENU ADD {}'.format(_quote_for_menu(path)))



def _menu_del(path):
    try:
        hexchat.command('MENU DEL {}'.format(_quote_for_menu(path)))
    except Exception:
        pass



def _strip_outer_quotes(value):
    cleaned = (value or '').strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in ('"', "'"):
        return cleaned[1:-1]
    return cleaned
  
def _choose_file_with_gtk():
    dialog = Gtk.FileChooserDialog(
        title='Select file to share',
        action=Gtk.FileChooserAction.OPEN,
    )
    dialog.add_buttons(
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN,
        Gtk.ResponseType.OK,
    )
    dialog.set_modal(True)

    filename = None
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()

    dialog.destroy()
    return filename



def _choose_file_with_tk():
    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()
    filename = filedialog.askopenfilename(title='Select file to share')
    root.destroy()
    return filename or None



def _choose_file():
    if GTK_AVAILABLE:
        return _choose_file_with_gtk()

    if TK_AVAILABLE:
        return _choose_file_with_tk()

    raise RuntimeError('No GUI file chooser is available. Install PyGObject or Tkinter, or use /0X0SHARE <full-path>.')



def _preferences_with_gtk():
    dialog = Gtk.Dialog(title='0x0 Share Preferences')
    dialog.set_modal(True)
    dialog.add_buttons(
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OK,
        Gtk.ResponseType.OK,
    )

    box = dialog.get_content_area()
    box.set_spacing(8)
    box.set_border_width(12)

    label = Gtk.Label(label='0x0-compatible upload host:')
    label.set_xalign(0.0)
    entry = Gtk.Entry()
    entry.set_text(_get_endpoint())
    entry.set_activates_default(True)
    dialog.set_default_response(Gtk.ResponseType.OK)

    example = Gtk.Label(label='Example: https://0x0.st')
    example.set_xalign(0.0)

    box.add(label)
    box.add(entry)
    box.add(example)
    dialog.show_all()

    response = dialog.run()
    value = None
    if response == Gtk.ResponseType.OK:
        value = entry.get_text()

    dialog.destroy()
    return value



def _preferences_with_tk():
    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()
    value = simpledialog.askstring(
        '0x0 Share Preferences',
        '0x0-compatible upload host:',
        initialvalue=_get_endpoint(),
        parent=root,
    )
    root.destroy()
    return value



def _open_preferences_dialog():
    if GTK_AVAILABLE:
        return _preferences_with_gtk()

    if TK_AVAILABLE:
        return _preferences_with_tk()

    raise RuntimeError('No GUI toolkit is available for preferences. Use /0X0SHAREHOST <url> instead.')

def _escape_filename(value):
    return value.replace('\\', '\\\\').replace('"', '\\"')



def _build_connection(parsed_url):
    hostname = parsed_url.hostname
    if not hostname:
        raise RuntimeError('Upload host is missing a hostname.')

    if parsed_url.scheme == 'https':
        return http_client.HTTPSConnection(
            hostname,
            parsed_url.port or 443,
            timeout=300,
            context=ssl.create_default_context(),
        )

    return http_client.HTTPConnection(
        hostname,
        parsed_url.port or 80,
        timeout=300,
    )



def _upload_file(file_path, endpoint):
    parsed = urlparse(endpoint)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise RuntimeError('Invalid upload endpoint: {}'.format(endpoint))

    if not os.path.isfile(file_path):
        raise RuntimeError('Not a regular file: {}'.format(file_path))

    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    boundary = '----HexChat0x0Share{}'.format(uuid.uuid4().hex)

    request_path = parsed.path or '/'
    if parsed.query:
        request_path = '{}?{}'.format(request_path, parsed.query)

    header = (
        '--{boundary}\r\n'
        'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        'Content-Type: {mime_type}\r\n\r\n'
    ).format(
        boundary=boundary,
        filename=_escape_filename(filename),
        mime_type=mime_type,
    ).encode('utf-8')

    footer = ('\r\n--{}--\r\n'.format(boundary)).encode('utf-8')
    content_length = len(header) + os.path.getsize(file_path) + len(footer)

    connection = _build_connection(parsed)

    try:
        connection.putrequest('POST', request_path)
        connection.putheader('User-Agent', USER_AGENT)
        connection.putheader('Content-Type', 'multipart/form-data; boundary={}'.format(boundary))
        connection.putheader('Content-Length', str(content_length))
        connection.endheaders()

        connection.send(header)
        with open(file_path, 'rb') as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                connection.send(chunk)
        connection.send(footer)

        response = connection.getresponse()
        response_body = response.read().decode('utf-8', errors='replace').strip()

        if response.status < 200 or response.status >= 300:
            detail = response_body or response.reason or 'Upload failed'
            raise RuntimeError('HTTP {}: {}'.format(response.status, detail))

        if not response_body:
            raise RuntimeError('Upload server returned an empty response.')

        first_line = response_body.splitlines()[0].strip()
        parsed_response = urlparse(first_line)
        if parsed_response.scheme not in ('http', 'https') or not parsed_response.netloc:
            raise RuntimeError('Unexpected upload response: {}'.format(response_body))

        return first_line
    finally:
        try:
            connection.close()
        except Exception:
            pass



def _upload_worker(file_path, endpoint, context):
    try:
        url = _upload_file(file_path, endpoint)
        RESULTS.put({
            'ok': True,
            'path': file_path,
            'url': url,
            'context': context,
        })
    except Exception as exc:
        RESULTS.put({
            'ok': False,
            'path': file_path,
            'error': str(exc),
            'context': context,
        })



def _start_upload(file_path, context):
    endpoint = _get_endpoint()
    basename = os.path.basename(file_path)
    context.prnt('[0x0-share] Uploading {} to {} ...'.format(basename, endpoint))

    thread = threading.Thread(
        target=_upload_worker,
        args=(file_path, endpoint, context),
        name='0x0-share-upload',
    )
    thread.daemon = True
    thread.start()



def _process_results(_userdata):
    while True:
        try:
            item = RESULTS.get_nowait()
        except queue.Empty:
            break

        context = item.get('context') or hexchat.get_context()
        basename = os.path.basename(item.get('path', 'file'))

        if item.get('ok'):
            url = item['url']
            try:
                context.command('SAY {}'.format(url))
                context.prnt('[0x0-share] Shared {}: {}'.format(basename, url))
            except Exception:
                _plugin_print('Upload succeeded for {}, but sending to chat failed: {}'.format(basename, url))
        else:
            context.prnt('[0x0-share] Upload failed for {}: {}'.format(basename, item.get('error', 'Unknown error')))

    return True

def cmd_share(word, word_eol, _userdata):
    context = hexchat.get_context()
    if not _current_context_requires_target(context):
        _plugin_print('Open a channel or private message tab before sharing a file.')
        return hexchat.EAT_ALL

    file_path = None
    if len(word) > 1:
        file_path = _strip_outer_quotes(word_eol[1])
    else:
        try:
            file_path = _choose_file()
        except Exception as exc:
            _plugin_print(str(exc))
            return hexchat.EAT_ALL

    if not file_path:
        return hexchat.EAT_ALL

    if not os.path.isfile(file_path):
        context.prnt('[0x0-share] File does not exist: {}'.format(file_path))
        return hexchat.EAT_ALL

    _start_upload(file_path, context)
    return hexchat.EAT_ALL



def cmd_host(word, word_eol, _userdata):
    if len(word) < 2:
        _plugin_print('Current upload host: {}'.format(_get_endpoint()))
        return hexchat.EAT_ALL

    try:
        endpoint = _set_endpoint(_strip_outer_quotes(word_eol[1]))
        _plugin_print('Upload host set to {}'.format(endpoint))
    except Exception as exc:
        _plugin_print(str(exc))

    return hexchat.EAT_ALL



def cmd_preferences(_word, _word_eol, _userdata):
    try:
        value = _open_preferences_dialog()
    except Exception as exc:
        _plugin_print(str(exc))
        return hexchat.EAT_ALL

    if value is None:
        return hexchat.EAT_ALL

    try:
        endpoint = _set_endpoint(value)
        _plugin_print('Upload host set to {}'.format(endpoint))
    except Exception as exc:
        _plugin_print(str(exc))

    return hexchat.EAT_ALL



def cmd_reset(_word, _word_eol, _userdata):
    _reset_endpoint()
    _plugin_print('Upload host reset to {}'.format(DEFAULT_ENDPOINT))
    return hexchat.EAT_ALL



def unload_cb(_userdata):
    for path in MENU_PATHS[:2]:
        _menu_del(path)

    for path in reversed(MENU_PATHS[3:]):
        _menu_del(path)

    _menu_del(MENU_PATHS[2])


def _register_menus():
    _menu_add('$TAB/0x0 Share')
    _menu_add('$TAB/0x0 Share/Share File...', '0X0SHARE')
    _menu_add('$TAB/0x0 Share/Preferences...', '0X0SHARECONF')
    _menu_add('$TAB/0x0 Share/Reset Host to Default', '0X0SHARERESET')
    _menu_add('$CHAN/0x0 Share')
    _menu_add('$CHAN/0x0 Share/Share File...', '0X0SHARE')
    _menu_add('$CHAN/0x0 Share/Preferences...', '0X0SHARECONF')
    _menu_add('$CHAN/0x0 Share/Reset Host to Default', '0X0SHARERESET')


hexchat.hook_command(
    '0X0SHARE',
    cmd_share,
    help='Usage: /0X0SHARE [full-path] - Upload a file to the configured 0x0-compatible host and send the URL to the current tab.',
)
hexchat.hook_command(
    '0X0SHAREHOST',
    cmd_host,
    help='Usage: /0X0SHAREHOST [url] - Show or set the 0x0-compatible upload host.',
)
hexchat.hook_command(
    '0X0SHARECONF',
    cmd_preferences,
    help='Usage: /0X0SHARECONF - Open the 0x0 Share preferences dialog.',
)
hexchat.hook_command(
    '0X0SHARERESET',
    cmd_reset,
    help='Usage: /0X0SHARERESET - Reset the upload host to the default.',
)
hexchat.hook_timer(250, _process_results)
hexchat.hook_unload(unload_cb)

_register_menus()
_plugin_print('Loaded. Right-click a tab and choose “Share File via 0x0...”. Current host: {}'.format(_get_endpoint()))
