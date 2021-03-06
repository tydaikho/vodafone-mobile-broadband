# -*- coding: utf-8 -*-
# Copyright (C) 2006-2007  Vodafone
# Author:  Pablo Martí & Nicholas Herriot
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""Controllers for preferences"""

import gobject
import gtk
#from gtkmvc import Controller
from gui.contrib.gtkmvc import Controller

from wader.common.provider import NetworkProvider

from gui.consts import (CFG_PREFS_DEFAULT_BROWSER,
                              CFG_PREFS_DEFAULT_EMAIL,
                              CFG_SMS_VALIDITY_R1W, CFG_SMS_VALIDITY_R1D,
                              CFG_SMS_VALIDITY_R3D, CFG_SMS_VALIDITY_MAX)

from gui.translate import _
from gui.dialogs import show_warning_dialog
from gui.tray import tray_available

VALIDITY_DICT = {
     _('Maximum time').encode('utf8'): CFG_SMS_VALIDITY_MAX,
     _('1 week').encode('utf8'): CFG_SMS_VALIDITY_R1W,
     _('3 days').encode('utf8'): CFG_SMS_VALIDITY_R3D,
     _('1 day').encode('utf8'): CFG_SMS_VALIDITY_R1D,
}


class PreferencesController(Controller):
    """Controller for preferences"""

    def __init__(self, model, parent_ctrl):
        Controller.__init__(self, model)
        self.parent_ctrl = parent_ctrl
        # handler id of self.view['gnomekeyring_checkbutton']::toggled
        self._hid1 = None
        # handler id of self.view['show_icon_checkbutton']::toggled
        self._hid2 = None

    # setup on initialisation of the view. Make sure you call the setup methods
    # for all the tabs windows in the view.

    def register_view(self, view):
        Controller.register_view(self, view)
        self.setup_sms_tab()
        self.setup_user_prefs_tab()
        self.setup_mail_browser_tab()
        self.setup_usage_tab()
        # set up signals after init
        self.setup_signals()

    def get_default_smsc(self, imsi):
        try:
            # create a NetworkProvider object to query our Network DB
            provider = NetworkProvider()
            # ask for our network attributes based on what our SIM is
            nets = provider.get_network_by_id(imsi)
            if not len(nets):
                raise ValueError
            return nets[0].smsc
        except (TypeError, ValueError):
            return None
        finally:
            provider.close()

    def setup_sms_tab(self):
        # Setup the sms preferences to reflect what's in our model on startup

        # Setup the SMSC
        self.model.default_smsc = self.get_default_smsc(
                                                self.parent_ctrl.model.imsi)

        # Setup the alternate checkbox
        # remember that if 'use an alternative SMSC service centre' is False
        # we have to grey out 'SMSC preferences' and toggle the current value
        # so tell the view that he has to do that by checking the
        # show_smsc_preferences flag.

        self.view.setup_alternate_smsc_address(self.model.use_alternate_smsc,
                                                self.model.default_smsc,
                                                self.model.smsc_number)

        # ok lets populate the view of the sms profile box
        smsc_profile_box = gtk.ListStore(gobject.TYPE_STRING)
        _iter = smsc_profile_box.append([self.model.smsc_profile])
        self.view.setup_smsc_profile(smsc_profile_box, _iter,
                                                self.model.use_alternate_smsc)

        # validity period
        sms_validity_box = gtk.ListStore(gobject.TYPE_STRING)
        _iter = None
        for key, value in VALIDITY_DICT.items():
            if value == self.model.sms_validity:
                _iter = sms_validity_box.append([key])
            else:
                sms_validity_box.append([key])
        self.view.setup_sms_message_validity(sms_validity_box, _iter)

        # finally the sms confirmation checkbox
        self.view.setup_sms_confirmation_checkbox(self.model.sms_confirmation)

    def setup_user_prefs_tab(self):
        # setup the user preferences to reflect what's in our model on startup
        # remember that if 'show_icon_on_tray' is False we have to grey out
        # 'Close_window_app_to_tray' so tell the view that he has to do that
        # by checking the show_icon flag and passing this with sensitive flag.
        sensitive = self.model.show_icon

        self.view.setup_user_exit_without_confirmation(
            self.model.exit_without_confirmation)
        self.view.setup_user_show_icon_on_tray(self.model.show_icon)
        self.view.setup_user_close_window_minimize(self.model.close_minimizes)
        self.view.setup_user_close_window_minimize_enable(sensitive)
        self.view.setup_manage_my_pin(self.model.manage_pin)
        self.view.setup_user_use_global_menu(self.model.use_global_menu)

    def setup_usage_tab(self):
        # setup the usage tab to reflect what's in our model on startup
        self.view.setup_usage_max_traffic_value(self.model.max_traffic)
        self.view.setup_usage_threshold_value(self.model.traffic_threshold)
        self.view.setup_usage_notification_check(self.model.usage_notification)

    def setup_mail_browser_tab(self):
        # setup the mail and browser tab to reflect what's in model on startup

        # ok lets populate the view of the mail combo box and text box first
        mail_combo_box = gtk.ListStore(gobject.TYPE_STRING)
        _iter = mail_combo_box.append([CFG_PREFS_DEFAULT_EMAIL])
        custom_iter = mail_combo_box.append([_('Custom')])

        # ok lets get the value for the mail text box from the model if exists
        mail_text_box = self.model.mail
        active_set = (_iter if mail_text_box == CFG_PREFS_DEFAULT_EMAIL
                                   else custom_iter)
        # set the combo box in the view to show the values
        self.view.setup_application_mail_combo_box(mail_combo_box, active_set)
        # we have to set the text box if it's a custom value otherwise leave
        # blank and show the default.
        if mail_text_box != CFG_PREFS_DEFAULT_EMAIL:
            self.view.setup_application_mail_text_box(mail_text_box)

        # ok lets populate the view of the browser combo box and text box
        browser_combo_box = gtk.ListStore(gobject.TYPE_STRING)
        _iter = browser_combo_box.append([CFG_PREFS_DEFAULT_BROWSER])
        custom_iter = browser_combo_box.append([_('Custom')])

        # ok lets get the value for the browser text box from the model
        # if it exists
        browser_text_box = self.model.browser
        active_set = (_iter if browser_text_box == CFG_PREFS_DEFAULT_BROWSER
                                   else custom_iter)
        # set the combo box in the view to show values
        self.view.setup_application_browser_combo_box(browser_combo_box,
                                                      active_set)
        # we have to set the browser box if it's a custom value otherwise
        # leave blank and show the default
        if browser_text_box != CFG_PREFS_DEFAULT_BROWSER:
            self.view.setup_application_browser_text_box(browser_text_box)

    def setup_signals(self):
        # setting up the gnomekeyring checkbox

        def keyringtoggled_cb(checkbutton):
            """
            Callback for the gnomekeyring_checkbutton::toggled signal

            we are gonna try to import gnomekeyring beforehand, if we
            get an ImportError we will inform the user about what she
            should do
            """
            if checkbutton.get_active():
                try:
                    import gnomekeyring
                except ImportError:
                    # block the handler so the set_active method doesnt execute
                    # this callback again
                    checkbutton.handler_block(self._hid1)
                    checkbutton.set_active(False)
                    # restore handler
                    checkbutton.handler_unblock(self._hid1)
                    message = _("Missing dependency")
                    details = _(
"""To use this feature you need the gnomekeyring module""")
                    show_warning_dialog(message, details)
                    return True

        # keep a reference of the handler id
        self._hid1 = self.view['gnomekeyring_checkbutton'].connect('toggled',
                                                        keyringtoggled_cb)

        def show_icon_cb(checkbutton):
            if checkbutton.get_active():
                if not tray_available():
                    # block the handler so the set_active method doesnt
                    # executes this callback again
                    checkbutton.handler_block(self._hid2)
                    checkbutton.set_active(False)
                    # restore handler
                    checkbutton.handler_unblock(self._hid2)
                    message = _("Missing dependency")
                    details = _("""
To use this feature you need either pygtk >= 2.10 or the egg.trayicon module
""")
                    show_warning_dialog(message, details)
                    return True
                else:
                    self.view.setup_user_close_window_minimize_enable(True)
            else:
                self.view.setup_user_close_window_minimize_enable(False)

        # keep a reference of the handler id
        self._hid2 = self.view['show_icon_checkbutton'].connect('toggled',
                                                                show_icon_cb)

    # ------------------------------------------------------------ #
    #                       Signals Handling                       #
    # ------------------------------------------------------------ #

    def _on_traffic_entry_value_changed(self):
        max_traffic = self.view['maximum_traffic_entry'].get_value()
        threshold = self.view['threshold_entry'].get_value()
        if threshold > max_traffic:
            self.view['threshold_entry'].set_value(max_traffic)

    def on_maximum_traffic_entry_value_changed(self, widget):
        self._on_traffic_entry_value_changed()

    def on_threshold_entry_value_changed(self, widget):
        self._on_traffic_entry_value_changed()

    def on_usage_notification_check_toggled(self, widget):
        self.view['threshold_entry'].set_sensitive(widget.get_active())

    def on_preferences_ok_button_clicked(self, widget):
        # ----- first tab -----
        # lets fetch all the values stored in the view for the first tab
        # and place them in the model.

        # get the sms validity first
        sms_validity_view = self.view['validity_combobox']
        model = sms_validity_view.get_model()
        _iter = sms_validity_view.get_active_iter()
        if _iter is not None:
            validity_option = model.get_value(_iter, 0)
            self.model.sms_validity = VALIDITY_DICT[validity_option]

        # SMS confirmation checkbox
        sms_confirmation = self.view['sms_confirmation'].get_active()
        self.model.sms_confirmation = sms_confirmation

        # get the 'use an alternative smsc address' and save to config.
        # If this is set 'true' then we should not bother saving details for
        # profile or smsc number, so first get the value from the view.
        alternate_sms_checkbox = \
                self.view['smsc_profile_checkbutton'].get_active()
        # Now set the model to that value.
        self.model.use_alternate_smsc = alternate_sms_checkbox

        # OK only set the SMSC values if the alternate_sms_checkbox is true.
        if alternate_sms_checkbox == True:
            smsc_profile_view = self.view['sms_profiles_combobox'].get_model()
            _iter = self.view['sms_profiles_combobox'].get_active_iter()
            smsc_profile_option = smsc_profile_view.get_value(_iter, 0)

            # ok lets set the model to the value in the view
            self.model.smsc_profile = smsc_profile_option

            # now get the smsc number from the view and set the model.browser
            smsc_number = self.view['smsc_number'].get_text()
            self.model.smsc_number = smsc_number

        # ----- second tab -----
        # lets fetch all the vaules stored in the view for the second tab.
        exit_without_confirmation = \
              self.view['exit_without_confirmation_checkbutton'].get_active()
        close_minimizes = self.view['close_window_checkbutton'].get_active()
        show_icon = self.view['show_icon_checkbutton'].get_active()
        manage_pin = self.view['gnomekeyring_checkbutton'].get_active()

        # set the model with those values.
        self.model.exit_without_confirmation = exit_without_confirmation
        self.model.close_minimizes = close_minimizes
        self.model.show_icon = show_icon
        self.model.manage_pin = manage_pin
        self.model.use_global_menu = self.view['use_global_menu'].get_active()

        # make the change in the parent
        if self.model.show_icon:
            self.parent_ctrl._setup_trayicon(ignoreconf=True)
        else:
            self.parent_ctrl._detach_trayicon()

        # ------third tab -----
        # fetch the browser combo box data + the browser custom drop down list
        browser_combo_view = self.view['browser_combobox'].get_model()
        _iter = self.view['browser_combobox'].get_active_iter()
        browser_options = browser_combo_view.get_value(_iter, 0)

        # ok if the guy selects the xdg-open just save that name value pair in
        # the model otherwise save the entry in the command box
        browser_command = self.view['browser_entry'].get_text()
        if browser_options != CFG_PREFS_DEFAULT_BROWSER and browser_command:
            self.model.browser = browser_command
        else:
            self.model.browser = CFG_PREFS_DEFAULT_BROWSER

        # fetch the mail combo box data and the mail custom drop down list
        mail_combo_view = self.view['mail_combobox'].get_model()
        _iter = self.view['mail_combobox'].get_active_iter()
        mail_options = mail_combo_view.get_value(_iter, 0)

        # ok if the guy selects the xdg-email just save that name
        # value pair in the model otherwise save the entry in the comand box
        mail_command = self.view['mail_entry'].get_text()
        if mail_options != CFG_PREFS_DEFAULT_EMAIL and mail_command:
            self.model.mail = mail_command
        else:
            self.model.mail = CFG_PREFS_DEFAULT_EMAIL

        # ----- fourth tab -----
        # get the value from the view and set the model
        max_traffic = self.view['maximum_traffic_entry'].get_value()
        self.model.max_traffic = max_traffic

        # get the value from the view and set the model
        threshold = self.view['threshold_entry'].get_value()
        self.model.traffic_threshold = threshold

        # get the value from the view and set the model
        usage_notification = self.view['usage_notification_check'].get_active()
        self.model.usage_notification = usage_notification

        # ok lets ask the model to save those items
        self.model.save()
        self._hide_ourselves()
        # check threshold after changing values.
        self.parent_ctrl.model.check_transfer_limit()
        # update usage view even if there is no connection active.
        self.parent_ctrl.update_usage_view()

    def on_preferences_cancel_button_clicked(self, widget):
        self._hide_ourselves()

    def _hide_ourselves(self):
        self.model.unregister_observer(self)
        self.view.hide()

    def on_custom_smsc_profile_checkbutton_toggled(self, button):
        self.model.use_alternate_smsc = button.get_active()
        self.view.setup_alternate_smsc_address(self.model.use_alternate_smsc,
                                                self.model.default_smsc,
                                                self.model.smsc_number)

    def on_browser_combobox_changed(self, combobox):
        model = combobox.get_model()
        iter = combobox.get_active_iter()
        if model.get_value(iter, 0) == CFG_PREFS_DEFAULT_BROWSER:
            self.view['hbox6'].set_sensitive(False)
        else:
            self.view['hbox6'].set_sensitive(True)

    def on_mail_combobox_changed(self, combobox):
        model = combobox.get_model()
        iter = combobox.get_active_iter()
        if model.get_value(iter, 0) == CFG_PREFS_DEFAULT_EMAIL:
            self.view['hbox7'].set_sensitive(False)
        else:
            self.view['hbox7'].set_sensitive(True)
