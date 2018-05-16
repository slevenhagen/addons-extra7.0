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
from openerp import netsvc
from datetime import datetime, timedelta

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if context is None:
            context = {}
        IDS =[]
        
        if context.get('search_order_lines', False):
            order_line_ids = context.get('search_order_lines')
            order_line_obj = self.pool.get('purchase.order.line')
            
            IDS = [lines.order_id.id for lines in order_line_obj.browse(cr,uid, order_line_ids,context=context)]
            
            
            if IDS:
                args += [('id', 'in', IDS)]

        return super(purchase_order, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'internal_number':'/'})
        return super(purchase_order, self).copy(cr, uid, id,
                default, context=context)
