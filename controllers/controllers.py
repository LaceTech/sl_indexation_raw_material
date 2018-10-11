# -*- coding: utf-8 -*-
from odoo import http

# class SlIndexationCost(http.Controller):
#     @http.route('/sl_indexation_cost/sl_indexation_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sl_indexation_cost/sl_indexation_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sl_indexation_cost.listing', {
#             'root': '/sl_indexation_cost/sl_indexation_cost',
#             'objects': http.request.env['sl_indexation_cost.sl_indexation_cost'].search([]),
#         })

#     @http.route('/sl_indexation_cost/sl_indexation_cost/objects/<model("sl_indexation_cost.sl_indexation_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sl_indexation_cost.object', {
#             'object': obj
#         })