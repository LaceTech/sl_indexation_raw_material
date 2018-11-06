# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging

_logger = logging.getLogger(__name__)


class IndexationRawMaterial(models.Model):
    _name = 'indexation.raw_material'
    _description = 'Indexation data about raw material'
