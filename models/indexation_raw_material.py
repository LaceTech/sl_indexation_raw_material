# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging
import threading

_logger = logging.getLogger(__name__)


class IndexationRawMaterial(models.Model):
    _name = 'indexation.raw_material'
    _description = 'Indexation data about raw material'


class IndexationRawMaterialLines(models.Model):
    _name = 'indexation.raw_material.lines'
    _description = 'Raw material indexation lines'

    # _order = "purchase_order_id"

    def update_indexation_raw_material_lines(self):
        try:
            _logger.info('algo success')
        except:
            _logger.error('algo failed')

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    indexation_value = fields.Float('Indexation Value', default=0., required=True)
    active = fields.Boolean('Active', default=True,
                            help="Uncheck the active field to disable an indexation value without deleting it.")


class IndexationRawMaterialLogLines(models.Model):
    _name = 'indexation.raw_material.log.lines'
    _description = 'Log and error about indexation raw material algorithm execution.'

    message = fields.Text()


class IndexationRawMaterialWizard(models.TransientModel):
    _name = 'indexation.raw_material.compute.all'
    _description = 'Compute all indexation of raw material'

    @api.multi
    def _algo_indexation_raw_material_all(self):
        _logger.info('Running algorithm indexation of raw material.')
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))

            self.env['indexation.raw_material.log.lines'].create({'message': "test"})
            self.env['indexation.raw_material.lines'].create({'indexation_value': 0.5})

            new_cr.commit()
            new_cr.close()
            return {}

    @api.multi
    def compute_indexation_raw_material(self):
        threaded_compute = threading.Thread(target=self._algo_indexation_raw_material_all, args=())
        threaded_compute.start()
        return {'type': 'ir.actions.act_window_close'}
