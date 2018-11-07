# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging
import threading

# import random

_logger = logging.getLogger(__name__)


class IndexationRawMaterialComputeWizard(models.TransientModel):
    _name = 'indexation.raw_material.compute.all'
    _description = 'Compute all indexation of raw material'

    @api.multi
    def compute_indexation_raw_material(self):
        # threaded_compute = threading.Thread(target=self._compute_indexation_raw_material, args=())
        # threaded_compute.start()
        self._compute_indexation_raw_material()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def apply_indexation_raw_material(self):
        # threaded_compute = threading.Thread(target=self._apply_indexation_raw_material, args=())
        # threaded_compute.start()
        self._apply_indexation_raw_material()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _compute_indexation_raw_material(self):
        _logger.info('Running algorithm indexation of raw material.')
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))

            _logger.warning("Not implemented.")
            msg = {'message': "Not implemented - fct algo_indexation_raw_material_all in wizard Compute indexation.",
                   'level': 3}
            self.env['indexation.raw_material.log.lines'].create(msg)

            # for i in range(20):
            #     self.env['indexation.raw_material.log.lines'].create({'message': "test"})
            #     self.env['indexation.raw_material.lines'].create({'indexation_value': random.uniform(0.4, 10.2)})

            new_cr.commit()
            new_cr.close()
            return {}

    @api.multi
    def _apply_indexation_raw_material(self):
        _logger.info('Running algorithm indexation of raw material.')
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))

            lst_category = self.env['product.category'].search([('enable_indexation_raw_material', '=', True)])
            for category in lst_category:
                self.env['indexation.raw_material'].apply_indexation(category)

            new_cr.commit()
            new_cr.close()
            return {}
