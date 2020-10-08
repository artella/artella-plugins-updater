#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utils functions for Artella Updater
"""

import os
import ssl
import sys
import math
import json
import logging
import tarfile
from datetime import datetime

try:
    from urllib.parse import urlparse, urlencode, urlunparse
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urlparse import urlparse, urlunparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError, URLError

import artella.dcc as dcc
from artella.core import qtutils, utils

if qtutils.QT_AVAILABLE:
    from artella.externals.Qt import QtCore

logger = logging.getLogger('artella')


def get_pypi_info(plugin_id):

    pypi_url = 'https://pypi.org/pypi/{}/json'.format(plugin_id)
    req = Request(pypi_url)

    rsp = None
    pypi_info = dict()
    try:
        rsp = urlopen(req)
    except URLError as exc:
        if hasattr(exc, 'reason'):
            msg = 'Failed to retrieve Plugin {} PyPI information ({}): "{}"'.format(plugin_id, pypi_url, exc.reason)
        elif hasattr(exc, 'code'):
            msg = 'Failed to retrieve Plugin {} PyPI information ({}): "{}"'.format(plugin_id, pypi_url, exc.code)
        else:
            msg = exc
        logger.debug(exc)
        logger.error(msg)
    if not rsp:
        return pypi_info

    plugin_pypi_rsp = rsp.read()
    if not plugin_pypi_rsp:
        return pypi_info

    plugin_pypi_data = json.loads(plugin_pypi_rsp)
    if not plugin_pypi_data:
        return pypi_info

    plugin_pypi_info = plugin_pypi_data.get('info', dict())
    if not plugin_pypi_info:
        return pypi_info

    pypi_info['author'] = plugin_pypi_info.get('author', '')
    pypi_info['author_email'] = plugin_pypi_info.get('author_email', '')
    pypi_info['summary'] = plugin_pypi_info.get('summary', '')
    pypi_info['version'] = plugin_pypi_info.get('version', '')

    plugin_pypi_releases = plugin_pypi_data.get('releases', dict())
    release_info = plugin_pypi_releases.get(pypi_info['version'], list())
    release = None
    for release_data in release_info:
        release_filename = release_data.get('filename', '')
        if release_filename.endswith('.tar.gz'):
            release = release_data
            break
    release_date = (release.get('upload_time', '') if release else '').split('T')[0].split('-')
    pypi_info['upload_date'] = datetime(*[int(date_token) for date_token in release_date]).strftime('%d %B %Y')
    pypi_info['size'] = convert_size(release.get('size', '') if release else '')
    pypi_info['url'] = release.get('url', '')

    return pypi_info


def convert_size(size_bytes):
    if size_bytes == 0 or size_bytes is None or size_bytes == '':
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return "%s %s" % (s, size_name[i])


def download_and_extract_package_from_pypi(url, file_path, install_path, max_retries=10):
    current_retry = 0
    while True:
        current_retry += 1
        if current_retry > max_retries:
            break
        try:
            file_data = urlopen(url)
            data_to_write = file_data.read()
            if not data_to_write:
                logger.warning('No data found in PyPI package: {}'.format(url))
                break
            with open(file_path, 'wb') as fh:
                fh.write(data_to_write)
                break
        except Exception as exc:
            logger.warning('Error while downloading PyPI package: {} | {}'.format(url, exc))
            return False

    if not os.path.isfile(file_path):
        return False
    valid_extract = True
    tar = tarfile.open(file_path, "r:gz")
    try:
        tar.extractall(install_path)
    except Exception as exc:
        logger.warning('Error while extracting PyPI package: {} | {}'.format(url, exc))
        valid_extract = False
    finally:
        tar.close()
    if not valid_extract:
        return False

    return True


def get_latest_stable_artella_dcc_plugin_info(dcc_name=None, platform=None, show_dialogs=False):
    """
    Returns plugin info data from Artella server

    :param str dcc_name: name of the DCC plugin we want to retrieve to retrieve info from. If not give current DCC
        will be used
    :param str platform: name of the OS platform we want to retrieve DCC plugin of (windows, darwin and linux)
    :return: Dictionary containing plugin info data
    :rtype: dict
    """

    dcc_plugin_info = dict()
    message_title = 'Impossible to retrieve version info'

    dcc_name = dcc_name or dcc.name()

    current_platform = platform or None
    if not current_platform:
        if utils.is_windows():
            current_platform = 'windows'
        elif utils.is_mac():
            current_platform = 'darwin'
        elif utils.is_linux():
            current_platform = 'linux'
    if not current_platform:
        msg = 'Impossible to retrieve Dcc plugin info from Artella server because ' \
              'current OS platform is not supported: "{}"'.format(sys.platform)
        logger.warning(msg)
        if show_dialogs:
            qtutils.show_warning_message_box(message_title, msg)
        return dcc_plugin_info

    artella_url = 'https://updates.artellaapp.com/plugins/{}/versions/stable-{}.json'.format(dcc_name, current_platform)
    req = Request(artella_url)

    rsp = None
    try:
        rsp = urlopen(req)
    except Exception:
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            # To avoid [SSL: CERTIFICATE_VERIFY_FAILED] errors.
            context = ssl._create_unverified_context()
            rsp = urlopen(req, context=context)
        except URLError as exc:
            if hasattr(exc, 'reason'):
                msg = 'Failed to retrieve Artella DCC plugin info ¨{}({})" from  Artella server ({}): "{}"'.format(
                    dcc_name, current_platform, artella_url, exc.reason)
            elif hasattr(exc, 'code'):
                msg = 'Failed to retrieve Artella DCC plugin info ¨{}({})" from  Artella server ({}): "{}"'.format(
                    dcc_name, current_platform, artella_url, exc.code)
            else:
                msg = exc
            logger.debug(exc)
            logger.error(msg)
            if show_dialogs:
                qtutils.show_error_message_box(message_title, msg)

    warning_message = 'Was not possible to retrieve DCC Artella plugin info ¨{}({})" from  Artella server'.format(
        dcc_name, current_platform)

    if not rsp:
        if show_dialogs:
            qtutils.show_warning_message_box(message_title, warning_message)
        return dcc_plugin_info

    artella_rsp = rsp.read()
    if not artella_rsp:
        if show_dialogs:
            qtutils.show_warning_message_box(message_title, warning_message)
        return dcc_plugin_info

    try:
        dcc_plugin_data = json.loads(artella_rsp)
    except Exception as exc:
        msg = 'Error while reading data from Artella DCC plugin info ¨{}({})": {}'.format(
            dcc_name, current_platform, exc)
        logger.error(msg)
        if show_dialogs:
            qtutils.show_error_message_box(message_title, msg)
        return dcc_plugin_info

    if not dcc_plugin_data:
        if show_dialogs:
            qtutils.show_warning_message_box(message_title, warning_message)
        return dcc_plugin_info

    dcc_plugin_info['platform'] = dcc_plugin_data.get('platform', '')
    dcc_plugin_info['version'] = dcc_plugin_data.get('version', '0.0.0')
    dcc_plugin_info['file_name'] = dcc_plugin_data.get('file_name', '')
    dcc_plugin_info['url'] = dcc_plugin_data.get('url', '')

    return dcc_plugin_info


if qtutils.QT_AVAILABLE:
    class UpdatePluginWorker(QtCore.QObject, object):

        updateStart = QtCore.Signal()
        updateFinish = QtCore.Signal(str)

        def __init__(self):
            super(UpdatePluginWorker, self).__init__()

            self.id = None
            self._package = None
            self._latest_version = None
            self._url = None
            self._install_path = None
            self._max_retries = 10

        def set_id(self, id):
            self._id = id

        def set_package(self, package):
            self._package = package

        def set_latest_version(self, latest_version):
            self._latest_version = latest_version

        def set_url(self, url):
            self._url = url

        def set_install_path(self, install_path):
            self._install_path = install_path

        def set_max_retries(self, value):
            self._max_retries = value

        def run(self):
            self.updateStart.emit()

            if not self._url or not self._url.endswith('.tar.gz'):
                error_msg = 'Plugin Package URL does not contains a .tar.gaz file ({} | {} | {}'.format(
                    self._id, self._latest_version, self._url)
                self.updateFinish.emit(error_msg)
                return

            # TODO: We should download to a temporal folder and once everything is extracted we should move the info to
            # TODO: its proper place

            base_file_name = '{}_{}'.format(self._id, self._latest_version)
            file_name = '{}.tar.gz'.format(base_file_name)
            file_path = os.path.join(self._install_path, file_name)

            try:
                valid = download_and_extract_package_from_pypi(
                    self._url, file_path, self._install_path, max_retries=self._max_retries)
                if not valid:
                    error_msg = 'Impossible to download and extract plugin from PyPI server ({} | {} | {})'.format(
                        self._id, self._latest_version, self._url)
                    self.updateFinish.emit(error_msg)
                    return
            except Exception as exc:
                error_msg = 'Error while downloading new plugin version from PyPI server ({} | {} | {} | {})'.format(
                        self._id, self._latest_version, self._url, exc)
                self.updateFinish.emit(error_msg)
                return False

            plugin_folder = None
            for root, dirs, files in os.walk(self._install_path):
                for plugin_dir in dirs:
                    if plugin_dir == self._package or plugin_dir == self._package.lower():
                        plugin_folder = os.path.join(root, plugin_dir)
                        break

            if not plugin_folder or not os.path.isdir(plugin_folder):
                error_msg = 'No Plugin folder found ({}) in the extracted Plugin data ({} | {})'.format(
                    self._package, self._id, self._latest_version)
                self.updateFinish.emit(error_msg)
                return

            self.updateFinish.emit('')
