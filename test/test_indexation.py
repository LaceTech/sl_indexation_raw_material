# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests.common import TransactionCase


class TestIndexation(TransactionCase):
    def __init__(self, *args, **kwargs):
        TransactionCase.__init__(self, *args, **kwargs)
        self.partner_id = []
        self.category_c = []
        self.product_p = []

    def setUp(self):
        # TODO : Validate if this function is necessary
        super(TestIndexation, self).setUp()
        self.partner_id = []
        self.category_c = []
        self.product_p = []

    def config_indexation(self, param, cant_categories, cant_products):
        """
            Set up values to be used to create the purchase order
            Use the result in our function to test the indexation functionality
        """

        print("Creating a Test customer for the PO")
        self.partner_id = self.env['res.partner'].create({
            'name': 'Customer A'
        })

        print("Creating {} categories".format(cant_categories))
        for category in range(cant_categories):
            self.category_c.append(self.env['product.category'].create({
                'name': 'Category ' + str(category),
                'enable_indexation_raw_material': True,
            }))

        print("Creating {} products and assign them a price".format(cant_products))
        for product in range(cant_products):
            if param == 1:
                self.product_p.append(self.env['product.template'].create({
                    'name': 'Product ' + str(product),
                    'list_price': 1000,
                    'standard_price': 1000,
                    'weight': 0.45675,
                    'volume': 1,
                }))
            else:
                self.product_p.append(self.env['product.template'].create({
                    'name': 'Product ' + str(product),
                    'list_price': random.randint(1, 1000),
                    'standard_price': random.randint(1, 1000),
                    'weight': random.random(),
                    'volume': random.randint(1, 10),
                }))

        print("Associate the category C to the product P.")
        if cant_categories != 0 and cant_products != 0:
            if cant_products > cant_categories:
                categ = 0
                for product in range(cant_products):
                    self.product_p[product].write({
                        'categ_id': self.category_c[categ].id,
                    })
                    if cant_categories - 1 == categ:
                        categ = 0
                    else:
                        categ = categ + 1
            else:
                for product in range(cant_categories):
                    self.product_p[product].write({
                        'categ_id': self.category_c[product].id,
                    })
                    if product == cant_products - 1:
                        break

    def test_indexation_defined_values(self):
        self.config_indexation(1, 1, 1)
        print("Defined Values")
        print("Creating a Purchase order PO and Associate the product P")
        product_variant = self.product_p[0].product_variant_id
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

        # print("Validating if we correct customer and product in the purchase order")
        # self.assertEqual(po.partner_id.name, 'Customer A')
        # print("------Customer and product validated correctly------")

        self.assertTrue(product_variant.id in po.order_line.mapped('product_id.id'))
        print("------Product Order validation correctly-------")

        # self.assertEqual(product_variant.list_price, 1000)
        # print("------Price validated correctly ---------")

        # Saving old value of indexation
        indexation_before = self.category_c[0].average_indexation
        print("------The validation of Indexation before the application is: {} ---------".format(
            indexation_before))

        po.button_confirm()

        # Saving new value of indexation
        indexation_after = self.category_c[0].average_indexation
        print("------The validation of Indexation after the application is: {} ---------".format(
            indexation_after))

        print("Comparing indexation value")
        self.assertNotEqual(indexation_after, indexation_before)
        print("------Indexation value are different ---------")
        # Validate that the price A changed after generating the indexation.
        # TODO: Validate it with Mathieu, the price of the product doesn't change
        self.assertNotEqual(product_variant.price, 1000, "The value of price are still the same")

    def test_indexation_random_values(self):
        self.config_indexation(2, 1, 1)
        print("Random Values")
        print("Creating a Purchase order PO and Associate the product P")
        product_variant = self.product_p[0].product_variant_id
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

        # print("Validating if we correct customer and product in the purchase order")
        # self.assertEqual(po.partner_id.name, 'Customer A')
        # print("------Customer and product validated correctly------")

        self.assertTrue(product_variant.id in po.order_line.mapped('product_id.id'))
        print("------Product Order validation correctly-------")

        # self.assertEqual(product_variant.list_price, 1000)
        # print("------Price validated correctly ---------")

        # Saving old value of indexation
        indexation_before = self.category_c[0].average_indexation
        print("------The validation of Indexation before the application is: {} ---------".format(
            indexation_before))

        po.button_confirm()

        # Saving new value of indexation
        indexation_after = self.category_c[0].average_indexation
        print("------The validation of Indexation after the application is: {} ---------".format(
            indexation_after))

        print("Comparing indexation value")
        self.assertNotEqual(indexation_after, indexation_before)
        print("------Indexation value are different ---------")
        # Validate that the price A changed after generating the indexation.
        # TODO: Validate it with Mathieu, the price of the product doesn't change
        self.assertNotEqual(product_variant.price, 1000, "The value of price are still the same")

    def test_indexation_multiple(self):
        self.setEnviroment(2, 5, 3)
        print("Multple Variables")
        print("Creating a Purchase order PO and Associate the product P")

        for c in self.category_c:
            products = filter(lambda x: x['categ_id'].id == c.id, self.product_p)
            listproducts = list(products)
            for p in listproducts:
                product_variant = p.product_variant_id

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

                self.assertTrue(product_variant.id in po.order_line.mapped('product_id.id'))
                print("------Product Order validation correctly-------")
                # Saving old value of indexation
                indexation_before = c.average_indexation
                print("------The validation of Indexation before the application is: {} ---------".format(
                    indexation_before))
                po.button_confirm()
                # Saving new value of indexation
                indexation_after = c.average_indexation
                print("------The validation of Indexation after the application is: {} ---------".format(
                    indexation_after))
                print("Comparing indexation value")
                self.assertNotEqual(indexation_after, indexation_before)
                print("------Indexation value are different ---------")
                # Validate that the price A changed after generating the indexation.
                # TODO: Validate it with Mathieu, the price of the product doesn't change
                self.assertNotEqual(product_variant.price, 1000, "The value of price are still the same")
