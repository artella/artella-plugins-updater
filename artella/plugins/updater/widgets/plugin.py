#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella Updater plugin implementation
"""

from __future__ import print_function, division, absolute_import

import os
import logging
import importlib

import artella
from artella.core import splash
from artella.plugins.updater import utils

from artella.externals.Qt import QtCore, QtWidgets, QtGui

logger = logging.getLogger('artella')


class PluginVersionWidget(QtWidgets.QFrame, object):
    updatePlugin = QtCore.Signal()
    updated = QtCore.Signal()

    def __init__(self, id, name, package, version, author, email, summary, latest_version, upload_date, size, url,
                 icon_pixmap=None, parent=None):
        super(PluginVersionWidget, self).__init__(parent)

        self._id = id
        self._name = name
        self._package = package
        self._version = version
        self._author = author
        self._email = email
        self._summary = summary
        self._latest_version = latest_version
        self._upload_date = upload_date
        self._size = size
        self._url = url

        icon_pixmap = (icon_pixmap or artella.ResourcesMgr().pixmap('artella') or QtGui.QPixmap()).scaled(
            QtCore.QSize(30, 30), QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setMinimumHeight(130)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)

        main_info_layout = QtWidgets.QVBoxLayout()
        main_info_layout.setContentsMargins(2, 2, 2, 2)
        main_info_layout.setSpacing(2)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(2, 2, 2, 2)
        top_layout.setSpacing(5)
        self._icon_label = QtWidgets.QLabel()
        self._icon_label.setPixmap(icon_pixmap)
        self._icon_label.setAlignment(QtCore.Qt.AlignTop)

        self._plugin_name_label = QtWidgets.QLabel(name)
        self._plugin_version_label = QtWidgets.QLabel('({})'.format(version))

        plugin_name_info_layout = QtWidgets.QVBoxLayout()
        plugin_name_info_layout.setContentsMargins(2, 2, 2, 2)
        plugin_name_info_layout.setSpacing(5)
        plugin_name_layout = QtWidgets.QHBoxLayout()
        plugin_name_layout.setContentsMargins(2, 2, 2, 2)
        plugin_name_layout.setSpacing(2)
        plugin_info_layout = QtWidgets.QHBoxLayout()
        plugin_info_layout.setContentsMargins(2, 2, 2, 2)
        plugin_info_layout.setSpacing(5)
        plugin_name_layout.addWidget(self._plugin_name_label)
        plugin_name_layout.addWidget(self._plugin_version_label)
        plugin_name_layout.addStretch()
        plugin_name_info_layout.addLayout(plugin_name_layout)
        plugin_name_info_layout.addLayout(plugin_info_layout)
        plugin_name_info_layout.addStretch()
        self._plugin_date_label = QtWidgets.QLabel(upload_date)
        self._plugin_size_label = QtWidgets.QLabel(size)
        separator_widget = QtWidgets.QWidget()
        separator_layout = QtWidgets.QVBoxLayout()
        separator_layout.setAlignment(QtCore.Qt.AlignLeft)
        separator_layout.setContentsMargins(0, 0, 0, 0)
        separator_layout.setSpacing(0)
        separator_widget.setLayout(separator_layout)
        separator_frame = QtWidgets.QFrame()
        separator_frame.setMaximumHeight(15)
        separator_frame.setFrameShape(QtWidgets.QFrame.VLine)
        separator_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_layout.addWidget(separator_frame)
        plugin_info_layout.addWidget(self._plugin_date_label)
        plugin_info_layout.addWidget(separator_widget)
        plugin_info_layout.addWidget(self._plugin_size_label)
        plugin_info_layout.addStretch()

        top_layout.addWidget(self._icon_label)
        top_layout.addLayout(plugin_name_info_layout)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(2, 2, 2, 2)
        bottom_layout.setSpacing(5)
        self._summary_text = QtWidgets.QPlainTextEdit(summary)
        self._summary_text.setReadOnly(True)
        self._summary_text.setMinimumHeight(60)
        self._summary_text.setFocusPolicy(QtCore.Qt.NoFocus)
        bottom_layout.addWidget(self._summary_text)

        download_layout = QtWidgets.QVBoxLayout()
        download_layout.setContentsMargins(2, 2, 2, 2)
        download_layout.setSpacing(2)
        self._progress = splash.ProgressCricle(width=80)
        self._progress_text = QtWidgets.QLabel('Wait please ...')
        self._ok_label = QtWidgets.QLabel()
        self._ok_label.setPixmap(artella.ResourcesMgr().pixmap('success'))
        self._update_button = QtWidgets.QPushButton()
        self._progress.setVisible(False)
        self._progress_text.setVisible(False)
        self._ok_label.setVisible(False)
        progress_layout = QtWidgets.QHBoxLayout()
        progress_layout.addStretch()
        progress_layout.addWidget(self._progress)
        progress_layout.addStretch()
        progress_text_layout = QtWidgets.QHBoxLayout()
        progress_text_layout.addStretch()
        progress_text_layout.addWidget(self._progress_text)
        progress_text_layout.addStretch()
        ok_layout = QtWidgets.QHBoxLayout()
        ok_layout.addStretch()
        ok_layout.addWidget(self._ok_label)
        ok_layout.addStretch()
        download_layout.addStretch()
        download_layout.addLayout(progress_layout)
        download_layout.addLayout(progress_text_layout)
        download_layout.addLayout(ok_layout)
        download_layout.addWidget(self._update_button)
        download_layout.addStretch()

        main_info_layout.addLayout(top_layout)
        main_info_layout.addStretch()
        main_info_layout.addLayout(bottom_layout)
        main_info_layout.addStretch()

        main_info_layout.addStretch()
        main_layout.addLayout(main_info_layout)
        separator_widget = QtWidgets.QWidget()
        separator_layout = QtWidgets.QVBoxLayout()
        separator_layout.setAlignment(QtCore.Qt.AlignLeft)
        separator_layout.setContentsMargins(0, 0, 0, 0)
        separator_layout.setSpacing(0)
        separator_widget.setLayout(separator_layout)
        separator_frame = QtWidgets.QFrame()
        separator_frame.setFrameShape(QtWidgets.QFrame.VLine)
        separator_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_layout.addWidget(separator_frame)
        main_layout.addWidget(separator_widget)
        main_layout.addLayout(download_layout)
        main_info_layout.addStretch()

        self._update_plugin_thread = QtCore.QThread(self)
        self._update_plugin_worker = utils.UpdatePluginWorker()
        self._update_plugin_worker.moveToThread(self._update_plugin_thread)
        self._update_plugin_worker.updateStart.connect(self._on_start_update)
        self._update_plugin_worker.updateFinish.connect(self._on_finish_update)
        self._update_plugin_thread.start()

        self._timer = QtCore.QTimer(self)

        self.updatePlugin.connect(self._update_plugin_worker.run)
        self._update_button.clicked.connect(self._on_update)
        self._timer.timeout.connect(self._on_advance_progress)

        self.refresh()

    def refresh(self):
        if self._latest_version == self._version:
            self._update_button.setText('Updated')
            self._update_button.setEnabled(False)
        else:
            self._update_button.setText('Update ({})'.format(self._latest_version))

    def _on_update(self):

        install_path = r'D:\dev\artella\test_download'

        plugin_path = self._id.replace('-', '.')
        try:
            mod = importlib.import_module(plugin_path)
        except Exception:
            mod = None
        if mod:
            install_path = os.path.dirname(mod.__path__[0])

        print(install_path)

        # self._update_plugin_worker.set_id(self._id)
        # self._update_plugin_worker.set_package(self._package)
        # self._update_plugin_worker.set_latest_version(self._latest_version)
        # self._update_plugin_worker.set_url(self._url)
        # self._update_plugin_worker.set_install_path(install_path)
        #
        # self.updatePlugin.emit()

    def _on_finish_update(self, error_msg):
        valid = not bool(error_msg)
        self._progress.setVisible(False)
        self._progress_text.setVisible(False)
        self._update_button.setVisible(not valid)
        self._ok_label.setVisible(valid)
        self.updated.emit()

    def _on_start_update(self):
        self._progress.setVisible(True)
        self._progress_text.setVisible(True)
        self._update_button.setVisible(False)
        self._ok_label.setVisible(False)
        self._timer.start(5)

    def _on_advance_progress(self):
        self._progress.setValue(self._progress.value() + 1)
