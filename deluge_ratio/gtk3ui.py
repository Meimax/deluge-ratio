# -*- coding: utf-8 -*-
# Copyright (C) 2020 PhasecoreX <phasecorex@gmail.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of Ratio and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging

import deluge.component as component
from deluge.common import get_pixmap
from deluge.plugins.pluginbase import Gtk3PluginBase
from deluge.ui.client import client
from gi.repository import Gtk

from .common import get_resource

log = logging.getLogger(__name__)


class Gtk3UI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource("config.ui"))

        component.get("Preferences").add_page(
            "Ratio", self.builder.get_object("prefs_box")
        )
        component.get("PluginManager").register_hook(
            "on_apply_prefs", self.on_apply_prefs
        )
        component.get("PluginManager").register_hook(
            "on_show_prefs", self.on_show_prefs
        )

        self.ratio_status_bar_ratio = component.get("StatusBar").add_item(
            image=get_pixmap("traffic16.png"),
            tooltip="Total Ratio",
        )

        self.ratio_status_bar_upload = component.get("StatusBar").add_item(
            image=get_pixmap("seeding16.png"),
            tooltip="Total Uploads",
        )

        self.ratio_status_bar_download = component.get("StatusBar").add_item(
            image=get_pixmap("downloading16.png"),
            tooltip="Total Downloads",
        )

        self.builder.connect_signals(
            {"on_reset_ratio_button_clicked": self.on_reset_ratio_button_clicked}
        )

    def disable(self):
        component.get("Preferences").remove_page("Ratio")
        component.get("PluginManager").deregister_hook(
            "on_apply_prefs", self.on_apply_prefs
        )
        component.get("PluginManager").deregister_hook(
            "on_show_prefs", self.on_show_prefs
        )

        component.get("StatusBar").remove_item(self.ratio_status_bar_ratio)
        component.get("StatusBar").remove_item(self.ratio_status_bar_upload)
        component.get("StatusBar").remove_item(self.ratio_status_bar_download)

    def update(self):
        client.ratio.get_ratio_and_totals().addCallback(self.update_ratio_label)

    def on_apply_prefs(self):
        log.debug("Applying prefs for Ratio")
        config = {"persistent": self.builder.get_object("persistent").get_active()}
        client.ratio.set_config(config)

    def on_show_prefs(self):
        client.ratio.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        """callback for on show_prefs"""
        self.builder.get_object("persistent").set_active(config["persistent"])

    def on_reset_ratio_button_clicked(self, widget):
        client.ratio.reset_ratio()

    def update_ratio_label(self, ratio_and_totals):
        self.ratio_status_bar_ratio.set_text(ratio_and_totals["ratio"])
        self.ratio_status_bar_upload.set_text(ratio_and_totals["upload"])
        self.ratio_status_bar_download.set_text(ratio_and_totals["download"])
