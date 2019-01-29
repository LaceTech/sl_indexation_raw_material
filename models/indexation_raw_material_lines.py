# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging

_logger = logging.getLogger(__name__)


class IndexationRawMaterialLines(models.Model):
    _name = 'indexation.raw_material.lines'
    _description = 'Raw material indexation lines'

    # _order = "purchase_order_id"

    @api.multi
    def enable_indexation_raw_material_lines(self, cxt):
        for record in self.browse(cxt['active_ids']):
            record.field_enable = True

    @api.multi
    def disable_indexation_raw_material_lines(self, cxt):
        for record in self.browse(cxt['active_ids']):
            record.field_enable = False

    @api.multi
    def compute_indexation_raw_material_lines(self, cxt):
        for record in self.browse(cxt['active_ids']):
            self.env['indexation.raw_material'].compute_indexation(po=record.purchase_id,
                                                                   indexation_raw_material_line=record)

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    category_id = fields.Many2one('product.category', 'Category')
    indexation_value = fields.Float('Indexation Value', default=0., required=True)
    product_qty = fields.Float("Product Quantity", default=0., required=True)
    field_enable = fields.Boolean('Enable', default=True,
                                  help="Uncheck to disable an indexation value without deleting it.")
