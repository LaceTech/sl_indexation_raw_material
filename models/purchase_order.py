# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Do indexation of raw material on purchase order when order is done."

    @api.multi
    def button_done(self):
        self.env['indexation.raw_material'].compute_indexation(lst_po=self)
        return super(PurchaseOrder, self).button_done()

    @api.multi
    def button_confirm(self):
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def button_unlock(self):
        return super(PurchaseOrder, self).button_unlock()
