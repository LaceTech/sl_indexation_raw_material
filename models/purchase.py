# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
import logging

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = "product.category"

    enable_indexation_raw_material = fields.Boolean(string="Enable indexation raw material",
                                                    help="Only for normal product.category, "
                                                         "enable indexation raw material.")
