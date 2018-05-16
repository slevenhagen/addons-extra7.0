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
# class procurement_order(osv.osv):
#     _inherit = 'procurement.order'
#     
#     def _get_related_procurements(self,cr,uid,ids,related_procurements,arg=None,context=None):
#         
#         res = {}
#         procurement_obj = self.pool.get('procurement.order')
#         stock_move = self.pool.get('stock.move')
#         for procurement in self.browse(cr,uid,ids):
# 
#             print procurement.location_id.id
#             location_id=procurement.location_id.id
#             product_id=procurement.product_id.id
#             
#             move_ids = stock_move.search(cr,uid,
#                        [('location_dest_id','=',location_id),
#                         ('product_id','=',product_id),
#                         ('state','not in',('done','canceled'))])
# #                       [('location_dest_id','=',12),('product_id','=',18)])
#             rel_procurements = procurement_obj.search(cr,uid,[('move_id','in',move_ids)])
#             res[procurement.id]= []
#             res[procurement.id].extend(rel_procurements)
#         print res
#         return res
#         
#         
#     _columns = { 'related_procurements' : fields.function(
#                 _get_related_procurements,
#                 type='one2many',
#                 obj='procurement.order',
#                 string='Related Procurements'),
#                 'location_id': fields.many2one('stock.location', 'Source Location', required=True, states={'draft':[('readonly',False)]}, readonly=True),
# 
#                 }
#===============================================================================
