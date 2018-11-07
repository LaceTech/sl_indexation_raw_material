# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Do indexation of raw material on purchase order when order is done."

    @api.multi
    def button_done(self):
        for po in self:
            self.env['indexation.raw_material'].compute_indexation(po=po)
        return super(PurchaseOrder, self).button_done()

    @api.multi
    def button_confirm(self):
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def button_unlock(self):
        return super(PurchaseOrder, self).button_unlock()

    @api.multi
    def compute_indexation_raw_material_on_po(self, cxt):
        for record in self.browse(cxt['active_ids']):
            self.env['indexation.raw_material'].compute_indexation(po=record)
