# -*- coding: utf-8 -*-
from odoo import http

# class SlIndexationRawMaterial(http.Controller):
#     @http.route('/sl_indexation_raw_material/sl_indexation_raw_material/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sl_indexation_raw_material/sl_indexation_raw_material/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sl_indexation_raw_material.listing', {
#             'root': '/sl_indexation_raw_material/sl_indexation_raw_material',
#             'objects': http.request.env['sl_indexation_raw_material.sl_indexation_raw_material'].search([]),
#         })

#     @http.route('/sl_indexation_raw_material/sl_indexation_raw_material/objects/<model("sl_indexation_raw_material.sl_indexation_raw_material"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sl_indexation_raw_material.object', {
#             'object': obj
#         })