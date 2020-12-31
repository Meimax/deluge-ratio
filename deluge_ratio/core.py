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

import deluge.component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase
from twisted.internet.task import LoopingCall

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    "persistent": True,
    "total_download": 0,
    "total_upload": 0,
}


class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("ratio.conf", DEFAULT_PREFS)
        self.config.run_converter((0, 1), 2, self.__migrate_config_1_to_2)
        self.config.save()

        if self.config["persistent"]:
            log.info("Restoring ratio values")
            self.total_download = self.config["total_download"]
            self.total_upload = self.config["total_upload"]
        else:
            self.total_download = 0
            self.total_upload = 0

        session = self.get_session_bytes()
        self.prev_net_recv_payload_bytes = session["net.recv_payload_bytes"]
        self.prev_net_sent_payload_bytes = session["net.sent_payload_bytes"]

        self.update_totals_timer = LoopingCall(self.update_totals)
        self.update_totals_timer.start(3)

        self.update_config_timer = LoopingCall(self.update_config)
        self.update_config_timer.start(321)

    def disable(self):
        self.update_totals_timer.stop()
        self.update_config_timer.stop()
        self.update_config()

    def update(self):
        pass

    def get_session_bytes(self):
        return deluge.component.get("Core").get_session_status(
            ["net.recv_payload_bytes", "net.sent_payload_bytes"]
        )

    def update_totals(self):
        session = self.get_session_bytes()
        self.total_download += (
            session["net.recv_payload_bytes"] - self.prev_net_recv_payload_bytes
        )
        self.total_upload += (
            session["net.sent_payload_bytes"] - self.prev_net_sent_payload_bytes
        )
        self.prev_net_recv_payload_bytes = session["net.recv_payload_bytes"]
        self.prev_net_sent_payload_bytes = session["net.sent_payload_bytes"]

    def update_config(self):
        """Write totals to the config."""
        if self.config["persistent"]:
            log.debug("Updating Ratio plugin config with current totals.")
            self.config["total_download"] = self.total_download
            self.config["total_upload"] = self.total_upload
            self.config.save()

    def __migrate_config_1_to_2(self, config):
        if "session_download" in config:
            del config["session_download"]
        if "session_upload" in config:
            del config["session_upload"]
        return config

    @export
    def set_config(self, config):
        """Set the config dictionary."""
        for key in config:
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Return the config dictionary."""
        return self.config.config

    @export
    def get_ratio_and_totals(self):
        """Generate the ratio and totals for the UI."""
        ratio = "∞"
        if self.total_download > 0:
            ratio = "{:.2f}".format(self.total_upload / self.total_download)
        return {
            "ratio": ratio,
            "upload": deluge.common.fsize(self.total_upload),
            "download": deluge.common.fsize(self.total_download),
        }

    @export
    def reset_ratio(self):
        """Reset the download and upload values."""
        self.total_download = 0
        self.total_upload = 0
        self.update_config()
