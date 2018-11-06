# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging
import threading
import random

_logger = logging.getLogger(__name__)


class IndexationRawMaterialComputeWizard(models.TransientModel):
    _name = 'indexation.raw_material.compute.all'
    _description = 'Compute all indexation of raw material'

    @api.multi
    def _algo_indexation_raw_material_all(self):
        _logger.info('Running algorithm indexation of raw material.')
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))

            for i in range(20):
                self.env['indexation.raw_material.log.lines'].create({'message': "test"})
                self.env['indexation.raw_material.lines'].create({'indexation_value': random.uniform(0.4, 10.2)})

            new_cr.commit()
            new_cr.close()
            return {}

    @api.multi
    def compute_indexation_raw_material(self):
        threaded_compute = threading.Thread(target=self._algo_indexation_raw_material_all, args=())
        threaded_compute.start()
        # self._algo_indexation_raw_material_all()
        return {'type': 'ir.actions.act_window_close'}
