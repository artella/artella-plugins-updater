#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains updater plugin widget implementation
"""

from __future__ import print_function, division, absolute_import

import logging

import artella
from artella.core import plugin, qtutils

logger = logging.getLogger('artella')


class UpdaterPlugin(plugin.ArtellaPlugin, object):

    ID = 'artella-plugins-updater'
    INDEX = 3

    def __init__(self, config_dict=None, manager=None):
        super(UpdaterPlugin, self).__init__(config_dict=config_dict, manager=manager)

    def check_for_updates(self):
        """
        Shows UI informing the user if there is available or not a new version of the DCC plugin to download
        """

        from artella.plugins.updater import utils
        from artella.plugins.updater.widgets import versioninfo

        latest_release_info = utils.get_latest_stable_artella_dcc_plugin_info(show_dialogs=True)
        if not latest_release_info:
            return False

        current_version = artella.DccPlugin().get_version()

        about_dialog = versioninfo.VersionInfoDialog(
            current_version=current_version, latest_release_info=latest_release_info)
        about_dialog.exec_()

        return True

    def updater(self):
        """
        Shows an about window that shows information about current installed Artella plugin
        """

        from artella.plugins.updater.widgets import updater

        if not qtutils.QT_AVAILABLE:
            logger.warning('Updater UI cannot be launched because Qt is not available!')
            return False

        updater_window = updater.UpdaterWindow()
        updater_window.show()

        return True
