# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _


#===============================================================================
# 
# class stock_picking(osv.osv):
#     _name = "stock.picking"
#     _inherit = ['stock.picking']
#     
#     def _get_related_procurements(self,cr,uid,ids,related_procurements,arg=None,context=None):
#         
#         res = {}
#         procurement_obj = self.pool.get('procurement.order')
#         stock_move = self.pool.get('stock.move')
#         
#         for stock_picking in self.browse(cr,uid,ids,context):
#            
#             stock_move_ids = [ rec.id for rec in stock_picking.move_lines]
#             
#             product_ids = [ rec.product_id.id for rec in stock_move.browse(cr,uid,stock_move_ids)]
#             procurement_ids = procurement_obj.search(cr,uid,
#                        [('product_id','in',product_ids),
#                         ('state','not in',('done','canceled'))]),
# #                       [('location_dest_id','=',12),('product_id','=',18)])
#             res[ids[0]]= procurement_ids
#         print res
#         return res
#         
# 
# 
#     _columns = { 'related_procurements' : fields.function(
#                 _get_related_procurements,
#                 type='one2many',
#                 obj='procurement.order',
#                 string='Related Procurements'),
#                 }
#===============================================================================

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = ['stock.move']
    
    _columns = { 'supply_method': fields.related('product_id','supply_method', type='many2one', relation='product.product', string='Supply Method')
                }
