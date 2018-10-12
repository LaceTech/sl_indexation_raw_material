# -*- coding: utf-8 -*-
{
    'name': "sl_indexation_raw_material",

    'summary': """Automatic product indexation by specific category of raw material.""",

    'description': """
        Execute indexation when a purchase order is completed to update the costs of 
        all products in a specific category.

        Indexation determines the costs of the raw materials by weight, finds an average cost, 
        and adjusts the costs of the products in a category.

        Change view :
        - Add field in category
    """,

    'author': "Mathben informatique",
    'website': "http://mathieubenoit.ca",
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
