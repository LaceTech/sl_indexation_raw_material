# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _


class IndexationRawMaterial(models.Model):
    _name = 'indexation.raw_material'
    _description = 'Indexation data about raw material'


class IndexationRawMaterialLogLines(models.Model):
    _name = 'indexation.raw_material.log.lines'
    _description = 'Log and error about indexation raw material algorithm execution.'

    message = fields.Text()


class IndexationRawMaterialLines(models.Model):
    _name = 'indexation.raw_material.lines'
    _description = 'Lines of each value of indexation data about raw material'
    # _order = "purchase_order_id"

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    indexation_value = fields.Float('Indexation Value', default=0., required=True)
    active = fields.Boolean('Active', default=True,
                            help="Uncheck the active field to disable an indexation value without deleting it.")
