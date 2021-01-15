#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains updater plugin widget implementation
"""

from __future__ import print_function, division, absolute_import

import logging

from artella.core import plugin, qtutils, dccplugin

logger = logging.getLogger('artella')


class UpdaterPlugin(plugin.ArtellaPlugin, object):

    ID = 'artella-plugins-updater'
    INDEX = 3

    def __init__(self, config_dict=None, manager=None):
        super(UpdaterPlugin, self).__init__(config_dict=config_dict, manager=manager)

    def check_for_updates(self, show_dialogs=True):
        """
        Shows UI informing the user if there is available or not a new version of the DCC plugin to download
        """

        from artella.plugins.updater import utils
        from artella.plugins.updater.widgets import versioninfo

        latest_release_info = utils.get_latest_stable_artella_dcc_plugin_info(show_dialogs=show_dialogs)
        if not latest_release_info:
            return False

        current_version = dccplugin.DccPlugin().get_version()

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

    def update_is_available(self, show_dialogs=True):
        """
        Returns whether or not a new Artella DCC plugin version is available to download
        :return:
        """

        from artella.plugins.updater import utils

        current_version = dccplugin.DccPlugin().get_version()
        if not current_version:
            return True
        latest_release_info = utils.get_latest_stable_artella_dcc_plugin_info(show_dialogs=show_dialogs)
        if not latest_release_info:
            return True
        latest_version = latest_release_info.get('version', None)
        if not latest_version:
            return True

        current_version_split = current_version.split('.')
        latest_version_split = latest_version.split('.')

        if latest_version_split[0] > current_version_split[0]:
            return True
        else:
            if latest_version_split[1] > current_version_split[1]:
                return True
            else:
                if latest_version_split[2] > latest_version_split[2]:
                    return True

        return False
