# -*- coding: utf-8 -*-
# Copyright (C) 2010  Vodafone Group
# Author:  Nicholas Herriot
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

from os.path import join

import gtk

from gui.contrib.gtkmvc import View
from gui.consts import APP_SLUG_NAME, GLADE_DIR, IMAGES_DIR, ANIMATION_DIR
from gui.translate import _


class PayAsYouTalkView(View):
    """View for the main Pay As You Talk window"""

    GLADE_FILE = join(GLADE_DIR, "payt.glade")
    sim_image = join(IMAGES_DIR, "simple_sim_35x20.png")
    payt_image = join(IMAGES_DIR, "topup-banner.png")
    creditcard_image = join(IMAGES_DIR, "credit_card_green.png")
    voucher_image = join(IMAGES_DIR, "voucher.png")
    voucher_throb = join(ANIMATION_DIR, "voucher.gif")
    payt_banner_voucher = join(ANIMATION_DIR, "topup-voucher-banner.gif")
    payt_banner_credit_check = join(ANIMATION_DIR,
                                    "topup-credit-check-banner.gif")

    def __init__(self, ctrl, parent_view):
        super(PayAsYouTalkView, self).__init__(ctrl, self.GLADE_FILE,
                                                'payt_window', parent_view,
                                                register=False,
                                                domain=APP_SLUG_NAME)
        self.setup_view()
        ctrl.register_view(self)

    def setup_view(self):
        self.get_top_widget().set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self['sim_image'].set_from_file(self.sim_image)
        self['paytbanner'].set_from_file(self.payt_image)
        self['credit_card_image'].set_from_file(self.creditcard_image)
        self['voucher_image'].set_from_file(self.voucher_image)

    def set_msisdn_value(self, value):
        if value is None:
            self['msisdn_view'].set_text(_("Unknown"))
        else:
            self['msisdn_view'].set_text(value)

    def enable_credit_button(self, sensitive):
        self['credit_button'].set_sensitive(sensitive)

    def set_credit_view(self, credit_value):
        self['credit_view'].set_text(credit_value)

    def set_credit_date(self, value):
        if value is None:
            self['date_view'].set_text(_("Unknown"))
        else:
            now = value.strftime("%c")
            self['date_view'].set_text(now)

    def enable_send_button(self, sensitive):
        self['voucher_button'].set_sensitive(sensitive)

    def clear_voucher_entry_view(self):
        # ok if the view has been asked to reset, make sure
        # we reset any previous messages too.
        self['voucher_code'].set_text('')
        self['voucher_response_message'].set_text('')

    def enable_voucher_entry_view(self, sensitive):
        self['voucher_code'].set_sensitive(sensitive)

    def get_voucher_code(self):
        # make sure we get the voucher code from the view
        voucher_code = self['voucher_code'].get_text().strip()
        return voucher_code

    def set_voucher_throbbing(self):
        self['voucher_image'].set_from_file(self.voucher_throb)

    def clear_voucher_throbbing(self):
        self['voucher_image'].set_from_file(self.voucher_image)

    def set_banner_voucher_animation(self):
        self['paytbanner'].set_from_file(self.payt_banner_voucher)

    def set_banner_credit_check_animation(self):
        self['paytbanner'].set_from_file(self.payt_banner_credit_check)

    def clear_banner_animation(self):
        self['paytbanner'].set_from_file(self.payt_image)
