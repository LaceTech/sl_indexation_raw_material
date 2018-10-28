# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _


class IndexationRawMaterial(models.Model):
    _name = 'indexation.raw_material'
    _description = 'Indexation data about raw material'
    # _order = "purchase_order_id"

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    indexation_value = fields.Float('Indexation Value', default=0., required=True)
    active = fields.Boolean('Active', default=True,
                            help="Uncheck the active field to disable an indexation value without deleting it.")
