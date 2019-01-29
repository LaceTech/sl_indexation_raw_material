# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Do indexation of raw material on purchase order when order is done."

    @api.multi
    def button_done(self):
        for po in self:
            self._do_compute_indexation(po)
        return super(PurchaseOrder, self).button_done()

    @api.multi
    def write(self, values):
        status = super(PurchaseOrder, self).write(values)
        if status:
            for po in self:
                if po.state in ["purchase", "done"]:
                    self._do_compute_indexation(po)
        return status

    @api.multi
    def button_confirm(self):
        for po in self:
            self._do_compute_indexation(po)
        return super(PurchaseOrder, self).button_confirm()

    # @api.multi
    # def button_unlock(self):
    #     return super(PurchaseOrder, self).button_unlock()

    @api.multi
    def compute_indexation_raw_material_on_po(self, cxt):
        for record in self.browse(cxt['active_ids']):
            self._do_compute_indexation(record)

    def _do_compute_indexation(self, po):
        status_info = self.env['indexation.raw_material'].compute_indexation(po=po)
        for po_id, po_dct_value in status_info.items():
            if po_id == po.id:
                msg = ""
                for cat_id, cat_dct_value in po_dct_value.items():
                    is_new = "old" not in cat_dct_value.keys()
                    if is_new:
                        msg += _("New indexation ")
                    else:
                        msg += _("Update indexation ")
                    msg += "<br/><ul>"
                    if is_new:
                        msg += "<li>" + _("indexation") + ": %s</li>" % cat_dct_value["new"]
                    else:
                        msg += "<li>" + _("indexation") + ": %s -> %s</li>" % (
                            cat_dct_value["old"], cat_dct_value["new"])
                    msg += "<li>" + _("Category id") + ": %s</li>" % cat_id
                    msg += "</ul>"

                    # Auto apply indexation
                    category_id = cat_dct_value["category"]
                    self.env['indexation.raw_material'].apply_indexation(category_id=category_id)
                if msg:
                    po.message_post(body=msg)
