# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging

_logger = logging.getLogger(__name__)


class IndexationRawMaterialLines(models.Model):
    _name = 'indexation.raw_material.lines'
    _description = 'Raw material indexation lines'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    category_id = fields.Many2one('product.category', 'Category')
    indexation_value = fields.Float('Indexation Value', default=0., required=True, digits=(16, 6))
    product_qty = fields.Float("Product Quantity", default=0., required=True)
    field_enable = fields.Boolean('Enable', default=True,
                                  help="Uncheck to disable an indexation value without deleting it.")
    purchase_write_date = fields.Datetime(compute='_compute_purchase_write_date')

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

        # apply indexation
        lst_category = self.env['product.category'].search([('enable_indexation_raw_material', '=', True)])
        for category in lst_category:
            self.env['indexation.raw_material'].apply_indexation(category)

    @api.multi
    def write(self, values):
        # Update purchase write data
        # values["purchase_write_date"] = self.purchase_id.write_date

        status = super(IndexationRawMaterialLines, self).write(values)

        # Apply indexation
        self.env['indexation.raw_material'].apply_indexation(self.category_id)

        return status

    @api.depends('purchase_id.write_date')
    def _compute_purchase_write_date(self):
        for record in self:
            record.purchase_write_date = record.purchase_id.write_date
