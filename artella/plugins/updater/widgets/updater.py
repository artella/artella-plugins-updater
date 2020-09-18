#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella Updater window implementation
"""

from __future__ import print_function, division, absolute_import

import os
import logging

import artella
import artella.dcc as dcc
from artella.core import utils as core_utils
from artella.plugins.updater import utils

from artella.externals.Qt import QtCore, QtWidgets, QtGui
from artella.plugins.updater.widgets import plugin

logger = logging.getLogger('artella')


class UpdaterWindow(artella.Window, object):
    def __init__(self, parent=None, **kwargs):
        super(UpdaterWindow, self).__init__(parent, **kwargs)

        self._plugins = dict()
        self._plugin_updated = False

        self.setWindowTitle('Artella Updater')

        self._fill_data()

        self.resize(self.minimumSizeHint())

    def closeEvent(self, event):
        if self._plugin_updated:
            dcc_name = dcc.name()
            import artella.loader
            artella.loader._reload()
            if dcc_name == 'maya':
                import maya.cmds as cmds
                cmds.evalDeferred(artella.loader.init)
            else:
                artella.loader.init()
        super(UpdaterWindow, self).closeEvent(event)

    def get_main_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        return main_layout

    def setup_ui(self):
        super(UpdaterWindow, self).setup_ui()

        self._package_tabs = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self._package_tabs)

    def _add_package_tab(self, package_name):
        package_widget = QtWidgets.QWidget()
        package_layout = QtWidgets.QVBoxLayout()
        package_layout.setContentsMargins(2, 2, 2, 2)
        package_layout.setSpacing(2)
        package_widget.setLayout(package_layout)
        package_scroll = QtWidgets.QScrollArea()
        package_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        package_scroll.setWidgetResizable(True)
        package_scroll.setWidget(package_widget)

        self._package_tabs.addTab(package_widget, package_name)

        return package_layout

    def _fill_data(self):

        install_path = r'D:\dev\artella\test_download'

        dcc_plugins = list()
        dcc_install_package = 'artella-installer-{}'.format(dcc.name())
        base_file_name = 'artella_installer_maya'
        file_name = '{}.tar.gz'.format(base_file_name)
        file_path = os.path.join(install_path, file_name)
        dcc_pypi_info = utils.get_pypi_info(dcc_install_package)
        if dcc_pypi_info:
            dcc_url = dcc_pypi_info.get('url', '')
            if dcc_url:
                valid = utils.download_and_extract_package_from_pypi(dcc_url, file_path, install_path)
                if valid:
                    config_file = None
                    print('Install Path: {}'.format(install_path))
                    for root, dirs, files in os.walk(install_path):
                        if config_file:
                            break
                        for file_path in files:
                            if file_path == 'artella-installer.json':
                                config_file = os.path.join(root, file_path)
                                break
                    if config_file and os.path.isfile(config_file):
                        config_data = core_utils.read_json(config_file)
                        config_plugins = config_data.get('plugins', list())
                        for config_plugin in config_plugins:
                            plugin_id = config_plugin.get('id', '')
                            if not plugin_id:
                                plugin_repo = config_plugin.get('repo', '')
                                if plugin_repo:
                                    plugin_id = plugin_repo.split('/')[-1]
                            if plugin_id:
                                dcc_plugins.append(plugin_id)
        dcc_plugins = list(set(dcc_plugins))

        plugins = artella.PluginsMgr().plugins
        for plugin_id, plugin_data in plugins.items():

            plugin_name = plugin_data['name']
            plugin_icon_name = plugin_data.get('icon', None)
            plugin_package = plugin_data.get('package', None)
            plugin_version = plugin_data.get('version', None)
            plugin_resource_paths = plugin_data.get('resource_paths', list())

            if plugin_id in dcc_plugins:
                dcc_plugins.remove(plugin_id)

            plugin_icon_pixmap = None
            if plugin_icon_name and plugin_resource_paths:
                for plugin_resource_path in plugin_resource_paths:
                    plugin_icon_path = os.path.join(plugin_resource_path, plugin_icon_name)
                    if os.path.isfile(plugin_icon_path):
                        plugin_icon_pixmap = QtGui.QPixmap(plugin_icon_path)

            if plugin_package not in self._plugins:
                package_layout = self._add_package_tab(plugin_package)
                self._plugins[plugin_package] = {'layout': package_layout, 'plugins': []}
            else:
                package_layout = self._plugins[plugin_package]['layout']

            pypi_info = utils.get_pypi_info(plugin_id)
            if not pypi_info:
                continue

            plugin_author = pypi_info.get('author', '')
            plugin_author_email = pypi_info.get('author_email', '')
            plugin_summary = pypi_info.get('summary', '')
            plugin_latest_version = pypi_info.get('version', '')    # this is the latest version of the plugin in PyPI
            plugin_upload_date = pypi_info.get('upload_date', '')
            plugin_size = pypi_info.get('size', '')
            plugin_url = pypi_info.get('url', '')

            new_plugin_widget = plugin.PluginVersionWidget(
                plugin_id, plugin_name, plugin_package, plugin_version, plugin_author, plugin_author_email,
                plugin_summary, plugin_latest_version, plugin_upload_date, plugin_size, plugin_url, plugin_icon_pixmap)
            new_plugin_widget.updated.connect(self._on_updated_plugin)
            self._plugins[plugin_package]['plugins'].append(new_plugin_widget)
            package_layout.addWidget(new_plugin_widget)

        print(dcc_plugins)

    def _on_updated_plugin(self):
        self._plugin_updated = True
