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
from openerp.tools.translate import _

class stock_move(osv.Model):
    _inherit = "stock.move"
    _columns = {
                'warranty': fields.float('Warranty (months)', readonly=True, help="Warranty as set on the product at the time of sale. This warranty field is used for computation of guarantee limit on RMA line and Repair Order instead of the warranty field on the product"),
               }

class sale_order(osv.Model):
    _inherit = "sale.order"
    def action_ship_create(self, cr, uid, ids, context=None):
#     def action_ship_create(self, cr, uid, ids, *args):
        ret = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)
        for sale_obj in self.browse(cr, uid, ids, context={}):
            for pick in sale_obj.picking_ids:  # sale_line_id
                for move in pick.move_lines:
                    warranty = move.sale_line_id and move.sale_line_id.product_id and  move.sale_line_id.product_id.warranty or 0.00
                    self.pool.get('stock.move').write(cr, uid, [move.id], {'warranty': warranty,
                                                                          'move_from_sales': True}, context={})
        return ret

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
