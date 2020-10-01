/**
 * Script: ratio.js
 *     The client-side javascript code for the Ratio plugin.
 *
 * Copyright:
 *     (C) PhasecoreX 2020 <phasecorex@gmail.com>
 *
 *     This file is part of Ratio and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */

RatioPlugin = Ext.extend(Deluge.Plugin, {
    constructor: function(config) {
        config = Ext.apply({
            name: 'Ratio'
        }, config);
        RatioPlugin.superclass.constructor.call(this, config);
    },

    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function() {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.RatioPage());
    }
});
new RatioPlugin();
