# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Do indexation of raw material on purchase order when order is done."

    @api.multi
    def button_done(self):
        """Update all product price in different category."""
        # validation
        print("test")

        # run purchase.order.button_done
        return super(PurchaseOrder, self).button_done()

    @api.multi
    def button_confirm(self):
        """Update all product price in different category."""
        # validation
        print("test")

        # run purchase.order.button_done
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def button_unlock(self):
        """Update all product price in different category."""
        # validation
        print("test")

        # run purchase.order.button_done
        return super(PurchaseOrder, self).button_unlock()
