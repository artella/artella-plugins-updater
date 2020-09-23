#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Updater version info widget implementation
"""

import logging
import webbrowser

import artella
import artella.dcc as dcc
from artella.core import qtutils

if qtutils.QT_AVAILABLE:
    from artella.externals.Qt import QtCore, QtWidgets, QtGui

logger = logging.getLogger('artella')


class VersionInfoDialog(artella.Dialog, object):
    def __init__(self, current_version, latest_release_info, parent=None, **kwargs):
        super(VersionInfoDialog, self).__init__(parent, **kwargs)

        self._current_version = current_version
        self._latest_release_info = latest_release_info

        self.setWindowTitle('Updater - Version Checker')

        self._fill_data()

    def get_main_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        return main_layout

    def setup_ui(self):
        super(VersionInfoDialog, self).setup_ui()

        versions_layout = QtWidgets.QHBoxLayout()
        versions_layout.setSpacing(2)
        versions_layout.setContentsMargins(0, 0, 0, 0)
        current_version_label = QtWidgets.QLabel('Current Version: ')
        self._current_version_label = QtWidgets.QLabel()
        latest_version_label = QtWidgets.QLabel('Latest Version: ')
        self._latest_version_label = QtWidgets.QLabel()
        versions_layout.addStretch()
        versions_layout.addWidget(current_version_label)
        versions_layout.addWidget(self._current_version_label)
        versions_layout.addStretch()
        versions_layout.addWidget(latest_version_label)
        versions_layout.addWidget(self._latest_version_label)
        versions_layout.addStretch()

        version_message_frame = QtWidgets.QFrame()
        version_message_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        version_message_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        version_message_layout = QtWidgets.QHBoxLayout()
        version_message_layout.setSpacing(2)
        version_message_layout.setContentsMargins(0, 0, 0, 0)
        version_message_frame.setLayout(version_message_layout)
        self._version_icon = QtWidgets.QLabel()
        self._version_message_label = QtWidgets.QLabel()
        version_message_layout.addStretch()
        version_message_layout.addWidget(self._version_icon)
        version_message_layout.addWidget(self._version_message_label)
        version_message_layout.addStretch()

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(2)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._go_to_download_web_btn = QtWidgets.QPushButton('Go to Artella Plugins website')
        buttons_layout.addWidget(self._go_to_download_web_btn)

        self.main_layout.addLayout(versions_layout)
        self.main_layout.addWidget(version_message_frame)
        self.main_layout.addLayout(buttons_layout)

        self._go_to_download_web_btn.clicked.connect(self._on_open_artella_plugins_webiste)

    def _fill_data(self):
        is_greater_version = self._is_greater_version()

        if is_greater_version:
            icon_pixmap = (artella.ResourcesMgr().pixmap('success') or QtGui.QPixmap()).scaled(
                QtCore.QSize(30, 30), QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            self._version_message_label.setText('Artella {} Plugin is updated!'.format(dcc.nice_name()))
        else:
            icon_pixmap = (artella.ResourcesMgr().pixmap('info') or QtGui.QPixmap()).scaled(
                QtCore.QSize(30, 30), QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            self._version_icon.setPixmap(icon_pixmap)
            self._version_message_label.setText('New Artella {} Plugin is available!'.format(dcc.nice_name()))

        self._version_icon.setPixmap(icon_pixmap)
        self._go_to_download_web_btn.setVisible(not is_greater_version)
        latest_version = self._latest_release_info.get('version', 'Undefined')
        self._current_version_label.setText(str(self._current_version or 'Undefined'))
        self._latest_version_label.setText(latest_version)

    def _is_greater_version(self):
        if not self._current_version:
            return False
        if not self._latest_release_info:
            return True

        latest_version = self._latest_release_info.get('version', None)
        if not latest_version:
            return True

        current_version_split = self._current_version.split('.')
        latest_version_split = latest_version.split('.')

        if latest_version_split[0] > current_version_split[0]:
            return False
        else:
            if latest_version_split[1] > current_version_split[1]:
                return False
            else:
                if latest_version_split[2] > latest_version_split[2]:
                    return False

        return True

    def _on_open_artella_plugins_webiste(self):

        artella_plugins_url = 'https://updates.artellaapp.com/'
        webbrowser.open(artella_plugins_url)
