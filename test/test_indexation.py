# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests.common import TransactionCase


class TestIndexation(TransactionCase):

    def setUp(self):
        super(TestIndexation, self).setUp()
        """
            Set up values to be used to create the purchase order
            Use the result in our function to test the indexation functionality
        """

        print("Creating a Test customer for the PO")
        self.partner_id = self.env['res.partner'].create({
            'name': 'Customer A'
        })

        print("Creating a category C*")
        self.category_c = self.env['product.category'].create({
            'name': 'Category C',
            'enable_indexation_raw_material': True,
        })

        print("Creating a product P* and assign it a price A*")
        self.product_p = self.env['product.template'].create({
            'name': 'Product P',
            'list_price': 1000,
            'standard_price': 1000,
            'weight': 0.45675,
            'volume': 1,
        })

        print("Associate the category C to the product P.")
        self.product_p.write({
            'categ_id': self.category_c.id,
        })

    def test_indexation(self):
        print("Creating a Purchase order PO and Associate the product P")
        product_variant = self.product_p.product_variant_id
        po = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'date_planned': fields.Date.today(),
            'order_line': [
                (0, 0, {
                    'product_id': product_variant.id,
                    'name': product_variant.name,
                    'product_qty': 1,
                    'product_uom': product_variant.uom_id.id,
                    'price_unit': product_variant.list_price,
                    'date_planned': fields.Date.today(), })],
        })

        print("Validating if we correct customer and product in the purchase order")
        self.assertEqual(po.partner_id.name, 'Customer A')
        print("------Customer and product validated correctly------")

        self.assertTrue(product_variant.id in po.order_line.mapped('product_id.id'))
        print("------Product Order validation correctly-------")

        self.assertEqual(product_variant.list_price, 1000)
        print("------Price validated correctly ---------")

        # Saving old value of indexation
        indexation_before = self.category_c.average_indexation
        print("------The validation of Indexation before the application is: {} ---------".format(
            indexation_before))

        po.button_confirm()

        # Saving new value of indexation
        indexation_after = self.category_c.average_indexation
        print("------The validation of Indexation after the application is: {} ---------".format(
            indexation_after))

        print("Comparing indexation value")
        self.assertNotEqual(indexation_after, indexation_before)
        print("------Indexation value are different ---------")
        # Validate that the price A changed after generating the indexation.
        # TODO: Validate it with Mathieu, the price of the product doesn't change
        self.assertNotEqual(product_variant.standard_price, 1000, "The value of price are still the same")
