# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    debug_raw_material_execution = fields.Selection([
        (0, "No debug"),
        (1, 'Show statistic')
    ], "Debug indexation raw material execution",
        help='Option to help execution debug when run indexation.')
