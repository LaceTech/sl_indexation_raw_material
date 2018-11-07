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
            _logger.warning(msg)
            return

        dct_category_to_compute = defaultdict(list)
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
            _logger.warning(msg)
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
                    _logger.error(msg)
                    continue

                # TODO include tax?
                # TODO use the same unit of measure
                # TODO use the same weight
                sum_price_unit_per_weight += order_line.price_unit / product_id.weight
                total_product += 1

            if total_product:
                new_indexation = sum_price_unit_per_weight / total_product

                # Try to find duplicate indexation_raw_material_line
                if indexation_raw_material_line is None:
                    lst_indexation_raw_material_line = self.env['indexation.raw_material.lines'].search([
                        ('purchase_id', '=', po.id), ('category_id', '=', categ_id.id)])
                    # if list is empty, create a new one
                    if len(lst_indexation_raw_material_line) == 1:
                        # Update it
                        indexation_raw_material_line = lst_indexation_raw_material_line[0]
                    else:
                        # Warning, duplicate of indexation_raw_material_line with same po
                        # Update the first one, but warning the user
                        indexation_raw_material_line = lst_indexation_raw_material_line[0]
                        index = -1
                        for item in lst_indexation_raw_material_line:
                            index += 1
                            if index == 0:
                                msg = {'message': "Duplicate indexation raw material line, check associated message.",
                                       'category_id': categ_id.id, 'purchase_id': po.id, 'indexation_line': item.id,
                                       'level': 3}
                            else:
                                item.field_enable = False
                                msg = {'message': "Duplicate indexation raw material line, check associated message. "
                                                  "DISABLED", 'category_id': categ_id.id, 'purchase_id': po.id,
                                       'indexation_line': item.id, 'level': 3}

                            self.env['indexation.raw_material.log.lines'].create(msg)
                            _logger.warning(msg)

                if indexation_raw_material_line:
                    # Check if value change
                    old_value = indexation_raw_material_line.indexation_value
                    has_update = old_value != new_indexation

                    # Update the indexation
                    indexation_raw_material_line.indexation_value = new_indexation
                    indexation_raw_material_line.category_id = categ_id
                    indexation_raw_material_line.field_enable = True

                    indexation_id = indexation_raw_material_line

                    if has_update:
                        _logger.info(
                            "Update new indexation_raw_material_line. po: %s, "
                            "old indexation_value: %s, new indexation_value: %s, category: %s." % (
                                po.id, old_value, new_indexation, categ_id.id))
                    else:
                        _logger.info("No update on indexation_raw_material_line. po: %s, indexation_value: %s, "
                                     "category: %s." % (po.id, new_indexation, categ_id.id))

                else:
                    # Create a new indexation
                    indexation = {'purchase_id': po.id, 'indexation_value': new_indexation, 'field_enable': True,
                                  'category_id': categ_id.id}
                    indexation_id = self.env['indexation.raw_material.lines'].create(indexation)
                    _logger.info(
                        "Create new indexation_raw_material_line. po: %s, indexation_value: %s, category: %s." % (
                            po.id, new_indexation, categ_id.id))

                # Create a log
                msg = {'message': "Find %s indexation." % new_indexation, 'category_id': categ_id.id,
                       'indexation_line': indexation_id.id, 'purchase_id': po.id, 'level': 2}
                self.env['indexation.raw_material.log.lines'].create(msg)
            else:
                # Create a warning
                msg = {'message': "Cannot compute indexation, item are empty. Check associated error.",
                       'category_id': categ_id.id, 'purchase_id': po.id, 'level': 3}
                self.env['indexation.raw_material.log.lines'].create(msg)
                _logger.warning(msg)

    @api.multi
    def apply_indexation(self):
        """Update all product cost with last indexation"""
        self.apply_indexation()
