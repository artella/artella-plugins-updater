#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella Updater plugin implementation
"""

from __future__ import print_function, division, absolute_import

import logging

import artella
from artella import dcc
from artella.core import dcc as core_dcc
from artella.core import plugin, utils, qtutils

if qtutils.QT_AVAILABLE:
    from artella.externals.Qt import QtWidgets

logger = logging.getLogger('artella')


class UpdaterPlugin(plugin.ArtellaPlugin, object):

    ID = 'artella-plugins-updater'
    INDEX = 3

    def __init__(self, config_dict=None, manager=None):
        super(UpdaterPlugin, self).__init__(config_dict=config_dict, manager=manager)

    def updater(self):
        """
        Shows an about window that shows information about current installed Artella plugin
        """

        updater_window = UpdaterWindow()
        updater_window.show()


class UpdaterWindow(artella.Window, object):
    def __init__(self, parent=None, **kwargs):
        super(UpdaterWindow, self).__init__(parent, **kwargs)

        self.setWindowTitle('Artella Updater')

    def get_main_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        return main_layout

    def setup_ui(self):
        super(UpdaterWindow, self).setup_ui()

