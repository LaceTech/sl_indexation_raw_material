# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class IndexationRawMaterial(models.Model):
    """
    Contain algorithm to compute indexation raw material.
    Create indexation raw material line with IndexationRawMaterialLines.
    Create log of the algorithm with IndexationRawMaterialLogLines.
    """
    _name = 'indexation.raw_material'
    _description = 'Indexation data about raw material'

    @api.multi
    def compute_and_apply_indexation(self):
        self.compute_indexation()
        self.apply_indexation()

    @api.multi
    def compute_indexation(self, po=None, indexation_raw_material_line=None):
        """
        Update all product price in different category.
        :param po: purchase order to find indexation
        :param indexation_raw_material_line: if not None, update this variable instead to create a new one
        :return: null
        """
        if po is None:
            # Create a warning
            msg = {'message': "Cannot compute indexation, purchase order is empty.", 'level': 3}
            if indexation_raw_material_line is not None:
                msg["indexation_line"] = indexation_raw_material_line.id
            self.env['indexation.raw_material.log.lines'].create(msg)
            return

        dct_category_to_compute = defaultdict(list)
        dct_category_result_price = defaultdict(float)
        # Fill dct_category_to_compute
        # Search order_line with product of right category to compute
        for element in po.order_line:
            product_id = element.product_id
            categ_id = product_id.categ_id
            if categ_id.enable_indexation_raw_material:
                dct_category_to_compute[categ_id].append(element)

        if not dct_category_to_compute:
            # Create a warning
            msg = {'message': "Cannot compute indexation, no purchase order line.", 'purchase_id': po.id, 'level': 3}
            if indexation_raw_material_line is not None:
                msg["indexation_line"] = indexation_raw_material_line.id
            self.env['indexation.raw_material.log.lines'].create(msg)
            return

        # Compute dct_category
        for categ_id, lst_order_line in dct_category_to_compute.items():

            sum_price_unit_per_weight = 0.
            total_product = 0
            # For each category, find unitary cost, divide by weight and sum all divide by nb article
            # Update indexation with last 4 results of the same category
            for order_line in lst_order_line:
                product_id = order_line.product_id
                # Validation
                # Check division by zero
                if product_id.weight == 0.:
                    # Create an error
                    msg = {'message': "Division by zero, field weight.", 'product_id': product_id.id,
                           'purchase_id': po.id, 'level': 4}
                    self.env['indexation.raw_material.log.lines'].create(msg)
                    continue

                # TODO include tax?
                # TODO use the same unit of measure
                # TODO use the same weight
                sum_price_unit_per_weight += order_line.price_unit / product_id.weight
                total_product += 1

            if total_product:
                new_indexation = sum_price_unit_per_weight / total_product

                if indexation_raw_material_line:
                    # Update the indexation
                    indexation_raw_material_line.indexation_value = new_indexation
                    indexation_raw_material_line.category_id = categ_id
                    indexation_id = indexation_raw_material_line
                else:
                    # Create a new indexation
                    indexation = {'purchase_id': po.id, 'indexation_value': new_indexation, 'field_enable': True,
                                  'category_id': categ_id}
                    indexation_id = self.env['indexation.raw_material.lines'].create(indexation)

                # Create a log
                msg = {'message': "Find %s indexation." % new_indexation, 'category_id': categ_id.id,
                       'indexation_line': indexation_id.id, 'purchase_id': po.id, 'level': 2}
                self.env['indexation.raw_material.log.lines'].create(msg)
            else:
                # Create a warning
                msg = {'message': "Cannot compute indexation, item are empty. Check associated error.",
                       'category_id': categ_id.id, 'purchase_id': po.id, 'level': 3}
                self.env['indexation.raw_material.log.lines'].create(msg)

    @api.multi
    def apply_indexation(self):
        """Update all product cost with last indexation"""
        self.apply_indexation()
