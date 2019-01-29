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

        # Create dictionary of category
        dct_category_to_compute = self._generate_dct_to_compute(po,
                                                                indexation_raw_material_line=
                                                                indexation_raw_material_line)
        if type(dct_category_to_compute) not in (dict, defaultdict):
            return

        # Compute dct_category
        self._calcul_indexation(po, dct_category_to_compute, indexation_raw_material_line=indexation_raw_material_line)

    @api.multi
    def apply_indexation(self, category_id=None):
        """Update all product cost with last indexation"""
        if category_id is None:
            # Create a warning
            msg = {'message': "Cannot apply indexation, product category is empty.", 'level': 3}
            self.env['indexation.raw_material.log.lines'].create(msg)
            _logger.warning(msg)
            return

        if not category_id.enable_indexation_raw_material:
            # Create a warning
            msg = {'message': "Cannot apply indexation when the indexation is disable."
                              "Check option 'enable_indexation_raw_material' in category.",
                   'category_id': category_id.id, 'level': 3}
            self.env['indexation.raw_material.log.lines'].create(msg)
            _logger.warning(msg)
            return

        indexation = category_id.average_indexation
        if indexation == 0.:
            # Create a warning
            msg = {'message': "Ignore to apply indexation when the indexation is 0.",
                   'category_id': category_id.id, 'level': 3}
            self.env['indexation.raw_material.log.lines'].create(msg)
            _logger.warning(msg)
            return

        lst_child_product = self.env['product.template'].search(
            [('categ_id', '=', category_id.id), ('active', '=', True)])

        # For information, find last indexation to understand the new difference
        total_item_old_indexation = 0
        sum_item_old_indexation = 0
        for product in lst_child_product:
            if product.weight != 0:
                total_item_old_indexation += 1
                # Reverse the product indexation by adding the ratio of the uom
                sum_item_old_indexation += (product.standard_price / product.weight) * product.uom_id.factor

            # Update new price
            product.standard_price = product.weight * indexation * product.uom_id.factor

        old_indexation = 0
        if total_item_old_indexation:
            old_indexation = sum_item_old_indexation / total_item_old_indexation

        if not lst_child_product:
            # Create a warning
            msg = {'message': "Cannot apply indexation when list of product is empty of category.",
                   'category_id': category_id.id, 'level': 3}
            self.env['indexation.raw_material.log.lines'].create(msg)
            _logger.warning(msg)
            return
        else:
            msg = {'message': "Apply %s indexation on %s product of category, old indexation %s." % (
                indexation, total_item_old_indexation, old_indexation), 'category_id': category_id.id, 'level': 2}
            self.env['indexation.raw_material.log.lines'].create(msg)
            _logger.info(msg)

    @api.multi
    def _generate_dct_to_compute(self, po, indexation_raw_material_line=None):
        dct_category_to_compute = defaultdict(list)
        # Fill dct_category_to_compute
        # Search order_line with product of right category to compute
        for element in po.order_line:
            product_id = element.product_id
            category_id = product_id.categ_id
            if category_id.enable_indexation_raw_material:
                dct_category_to_compute[category_id].append(element)

        if not dct_category_to_compute:
            # Create a warning
            msg = {'message': "Cannot compute indexation, no purchase order line.", 'purchase_id': po.id, 'level': 3}
            if indexation_raw_material_line is not None:
                msg["indexation_line"] = indexation_raw_material_line.id
            self.env['indexation.raw_material.log.lines'].create(msg)
            _logger.warning(msg)
            return
        return dct_category_to_compute

    @api.multi
    def _calcul_indexation(self, po, dct_category_to_compute, indexation_raw_material_line=None):
        for category_id, lst_order_line in dct_category_to_compute.items():
            sum_price_unit_per_weight = 0.
            total_product_qty = 0
            # For each category, find unitary cost, divide by weight and sum all divide by nb article
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

                # Reduce the product indexation by removing the ratio of the uom
                sum_price_unit_per_weight += (order_line.price_unit / product_id.weight) * \
                                             product_id.uom_id.factor_inv * order_line.product_qty
                total_product_qty += order_line.product_qty

            if total_product_qty:
                new_indexation = sum_price_unit_per_weight / total_product_qty
                _indexation_raw_material_line = None

                # Try to find duplicate indexation_raw_material_line
                if indexation_raw_material_line is None:
                    lst_indexation_raw_material_line = self.env['indexation.raw_material.lines'].search([
                        ('purchase_id', '=', po.id), ('category_id', '=', category_id.id)])
                    # if list is empty, create a new one
                    if len(lst_indexation_raw_material_line) == 1:
                        # Update it
                        _indexation_raw_material_line = lst_indexation_raw_material_line[0]
                    elif len(lst_indexation_raw_material_line) > 1:
                        # Warning, duplicate of indexation_raw_material_line with same po
                        # Update the first one, but warning the user
                        _indexation_raw_material_line = lst_indexation_raw_material_line[0]
                        index = -1
                        for item in lst_indexation_raw_material_line:
                            index += 1
                            if index == 0:
                                msg = {'message': "Duplicate indexation raw material line, check associated message.",
                                       'category_id': category_id.id, 'purchase_id': po.id, 'indexation_line': item.id,
                                       'level': 3}
                            else:
                                item.field_enable = False
                                msg = {'message': "Duplicate indexation raw material line, check associated message. "
                                                  "DISABLED", 'category_id': category_id.id, 'purchase_id': po.id,
                                       'indexation_line': item.id, 'level': 3}

                            self.env['indexation.raw_material.log.lines'].create(msg)
                            _logger.warning(msg)
                else:
                    _indexation_raw_material_line = indexation_raw_material_line

                if _indexation_raw_material_line:
                    # Update it
                    # Check if value change
                    old_indexation = _indexation_raw_material_line.indexation_value
                    has_update = not abs(new_indexation - old_indexation) < 0.00000001

                    # Update the indexation
                    _indexation_raw_material_line.indexation_value = new_indexation
                    _indexation_raw_material_line.category_id = category_id
                    _indexation_raw_material_line.field_enable = True
                    _indexation_raw_material_line.product_qty = total_product_qty

                    indexation_id = _indexation_raw_material_line

                    # Show to user if the indexation has difference
                    if has_update:
                        # Create a log
                        msg = {
                            'message': 'Update indexation %s, old indexation %s' % (new_indexation, old_indexation),
                            'category_id': category_id.id, 'indexation_line': indexation_id.id, 'purchase_id': po.id,
                            'level': 2}
                        self.env['indexation.raw_material.log.lines'].create(msg)
                        _logger.info(msg)
                    else:
                        # Create a log
                        msg = {
                            'message': 'No update on indexation_raw_material_line. Actual value: %s' % new_indexation,
                            'category_id': category_id.id, 'indexation_line': indexation_id.id, 'purchase_id': po.id,
                            'level': 2}
                        self.env['indexation.raw_material.log.lines'].create(msg)
                        _logger.info(msg)

                else:
                    # Create a new indexation
                    indexation = {'purchase_id': po.id, 'indexation_value': new_indexation, 'field_enable': True,
                                  'category_id': category_id.id, 'product_qty': total_product_qty}
                    indexation_id = self.env['indexation.raw_material.lines'].create(indexation)
                    # Create a log
                    msg = {'message': 'Create new indexation: %s' % new_indexation, 'category_id': category_id.id,
                           'indexation_line': indexation_id.id, 'purchase_id': po.id, 'level': 2}
                    self.env['indexation.raw_material.log.lines'].create(msg)
                    _logger.info(msg)

                # TODO hardcoded, use settings to set the max
                # Max 5 elements, remove the 6 and more, the oldest
                # Use the same list of indexation before
                lst_indexation_raw_material_line = self.env['indexation.raw_material.lines'].search(
                    [('category_id', '=', category_id.id), ('field_enable', '=', True)], order='write_date desc')
                if len(lst_indexation_raw_material_line) > 5:
                    for record in lst_indexation_raw_material_line[5:]:
                        record.field_enable = False
                        msg = {
                            'message': 'Disable indexation because more than 5.',
                            'category_id': category_id.id, 'indexation_line': indexation_id.id, 'purchase_id': po.id,
                            'level': 2}
                        self.env['indexation.raw_material.log.lines'].create(msg)
                        _logger.info(msg)
            else:
                # Create a warning
                msg = {'message': "Cannot compute indexation, item are empty. Check associated error.",
                       'category_id': category_id.id, 'purchase_id': po.id, 'level': 3}
                self.env['indexation.raw_material.log.lines'].create(msg)
                _logger.warning(msg)
