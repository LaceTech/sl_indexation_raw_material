# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging

_logger = logging.getLogger(__name__)


class IndexationRawMaterialCleanWizard(models.TransientModel):
    _name = 'indexation.raw_material.clean.all'
    _description = 'Clean all indexation of raw material'

    @api.multi
    def remove_disabled_indexation(self):
        self.env['indexation.raw_material.lines'].search([('field_active', '=', False)]).unlink()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def clean_all_indexation(self):
        self.env['indexation.raw_material.lines'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def clean_all_log(self):
        self.env['indexation.raw_material.log.lines'].search([]).unlink()
        return {'type': 'ir.actions.act_window_close'}
