# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _product_available_mo(self, cr, uid, ids,
                              field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        product_ids = []
        product_obj = self.pool.get('product.product')
        location = False
        for move in self.browse(cr, uid, ids, context=context):
            res[move.id] = {}.fromkeys(field_names, 0.0)
            location = move.location_id.id
            if move.product_id.id not in product_ids:
                product_ids.append(move.product_id.id) 
        for f in field_names:
            c = context.copy()
            if location:
                c.update({'location': location,})
            if f == 'qty_available_mo':
                c.update({'states': ('done',), 'what': ('in', 'out'),})
            if f == 'qty_virtual_mo':
                c.update({'states': ('confirmed','waiting','assigned','done'),
                          'what': ('in', 'out'),})
            stock = product_obj.\
                get_product_available(cr, uid, product_ids, context=c)
            for move in self.browse(cr, uid, ids, context=context):
                res[move.id][f] = stock.get(move.product_id.id, 0.0)
                if f == 'qty_virtual_mo':
                    res[move.id][f] += move.product_qty
        return res

    _columns = {
        'qty_available_mo': fields.function(_product_available_mo,
            multi='qty_available_mo',
            type='float', string='Available',
            digits_compute=dp.get_precision('Product Unit of Measure'),),
        'qty_virtual_mo': fields.function(_product_available_mo,
            multi='qty_virtual_mo',
            type='float', string='Virtual',
            digits_compute=dp.get_precision('Product Unit of Measure'),),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
