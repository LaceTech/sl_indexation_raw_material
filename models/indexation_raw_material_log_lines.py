# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging

_logger = logging.getLogger(__name__)


class IndexationRawMaterialLogLines(models.Model):
    _name = 'indexation.raw_material.log.lines'
    _description = 'Log and error about indexation raw material algorithm execution.'

    message = fields.Text()
    product_id = fields.Many2one('product.product', 'Product')
    category_id = fields.Many2one('product.category', 'Category')
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    indexation_line = fields.Many2one('indexation.raw_material.lines', 'Indexation line')
    level = fields.Selection([
        (0, "Info"),
        (1, "Debug"),
        (2, "Success"),
        (3, "Warning"),
        (4, "Error")
    ], "Log level", default=0, help='Log level: Info, Debug, Success, Warning, Error')
