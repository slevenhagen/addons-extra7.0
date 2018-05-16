# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time

class stock_partial_picking_line(osv.TransientModel):
    _inherit = "stock.partial.picking.line"
    _columns = {
#         'prod_received_qty': fields.float("Received Quantity"),
        'receive': fields.boolean('Receive'),
        }

    def receive_button(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'receive': True})
         
    def onchange_quantity(self, cr, uid, ids, quantity, receive):
        if receive:
            return {'value': {}}
        result = {}
        if quantity:
            result['quantity'] = quantity
            result['receive'] = True 
        return {'value': result}
    
#     def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#         #override of fields_view_get in order to change the label of the process button and the separator accordingly to the shipping type
#         if context is None:
#             context={}
#         res = super(stock_partial_picking_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
#         type = context.get('default_type', False)
#         if type:
#             doc = etree.XML(res['arch'])
#             for node in doc.xpath("//field[@name='receive']"):
#                 if type == 'in':
#                     node.set('string', _('_Receive'))
#                 elif type == 'out':
#                     node.set('string', _('_Ship'))
#             for node in doc.xpath("//separator[@name='product_separator']"):
#                 if type == 'in':
#                     node.set('string', _('Receive Products'))
#                 elif type == 'out':
#                     node.set('string', _('Deliver Products'))
#             res['arch'] = etree.tostring(doc)
#         return res
    
stock_partial_picking_line()

# class stock_partial_move_memory_in(osv.TransientModel):
#     _inherit = "stock.partial.picking.line"
#     _columns = {
# #         'prod_received_qty': fields.float("Received Quantity"),
#         'receive': fields.boolean('Receive'),
#         }
#     
#     def receive_button(self, cr, uid, ids, context):
#         return self.write(cr, uid, ids, {'receive': True})
#         
#     def onchange_quantity(self, cr, uid, ids, quantity, receive):
#         if receive:
#             return {'value': {}}
#         
#         result = {}
#         if quantity:
#             result['quantity'] = quantity
#             result['receive'] = True 
#         return {'value': result}
# 
# stock_partial_move_memory_in()=======

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:>>>>>>> MERGE-SOURCE
