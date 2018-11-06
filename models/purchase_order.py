# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Do indexation of raw material on purchase order when order is done."

    @api.multi
    def button_done(self):
        """Update all product price in different category."""
        dct_category_to_compute = defaultdict(list)
        dct_category_result_price = defaultdict(float)
        # Fill dct_category_to_compute
        # Search order_line with product of right category to compute
        for po in self:
            for element in po.order_line:
                product_id = element.product_id
                categ_id = product_id.categ_id
                if categ_id.enable_indexation_raw_material:
                    dct_category_to_compute[categ_id].append(element)

        # Compute dct_category
        for categ_id, lst_order_line in dct_category_to_compute.items():

            sum_price_unit_per_weight = 0.
            total_product = 0
            # For each category, find unitary cost, divide by weight and sum all divide by nb article
            # Update indexation with last 4 result of the same category
            for order_line in lst_order_line:
                product_id = order_line.product_id
                # Validation
                # Check division by zero
                if product_id.weight == 0.:
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
                msg = {'message': "Find %s indexation." % new_indexation, 'category_id': categ_id.id,
                       'purchase_id': po.id, 'level': 2}
                self.env['indexation.raw_material.log.lines'].create(msg)
            else:
                msg = {'message': "Cannot compute indexation, item are empty. Check associated error.",
                       'category_id': categ_id.id, 'purchase_id': po.id, 'level': 3}
                self.env['indexation.raw_material.log.lines'].create(msg)

        # TODO update all product cost for the category

        # run purchase.order.button_done
        return super(PurchaseOrder, self).button_done()

    @api.multi
    def button_confirm(self):
        """Update all product price in different category."""
        # run purchase.order.button_done
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def button_unlock(self):
        """Update all product price in different category."""
        # run purchase.order.button_done
        return super(PurchaseOrder, self).button_unlock()
