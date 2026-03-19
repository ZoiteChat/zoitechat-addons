# Copyright 2026 Jesse Rhodes <jesse@sney.ca>
# SPDX-License-Identifier: MIT

import hexchat

__module_name__ = 'Caller-Id logger'
__module_version__ = '1.0'
__module_description__ = 'Prints Libera.Chat/OFTC caller-id notifications to a dedicated tab'
# based on TingPing's highlight.py

TAB_NAME = '(caller-id)'

ALERT_TEXT_1 = 'Message request from '
ALERT_TEXT_2 = ', do you want to /accept?'

CID_MODES = ('+g', '+G', '+j')

def find_cidtab():
	context = hexchat.find_context(channel=TAB_NAME)
	if context == None: # Create a new one in the background
		newtofront = hexchat.get_prefs('gui_tab_newtofront')

		hexchat.command('set -quiet gui_tab_newtofront 0')
		hexchat.command('newserver -noconnect {0}'.format(TAB_NAME))
		hexchat.command('set -quiet gui_tab_newtofront {}'.format(newtofront))

		return hexchat.find_context(channel=TAB_NAME)
	else:
		return context

def cid_callback(word, word_eol, user_data):

	cid_context = find_cidtab()

	net = hexchat.get_info("network")
	# this returns what the network is called in servlist.conf, which might differ from the tab label

	for mode in CID_MODES:
		if mode in word_eol[0]:
			if net == 'OFTC':
				cid_context.prnt(ALERT_TEXT_1 + word[3] + " on " + net + ALERT_TEXT_2)
				break
			# OFTC combines nick and host in this message, e.g.:
			# --- nickname[~user@some.host] :is messaging or inviting you, and you are umode +g, +j, or +G.

			if net == 'Libera.Chat':
				cid_context.prnt(ALERT_TEXT_1 + word[3] + " (" + word[4] + ") on " + net + ALERT_TEXT_2)
				break
			# While Libera separates them:
			# --- nickname ~user@some.host :is messaging you, and you have umode +g. The message was discarded.

	return hexchat.EAT_ALL

hexchat.hook_server('718', cid_callback)
