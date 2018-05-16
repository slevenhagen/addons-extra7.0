# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def _emergency_line_to_create(self, cr, uid, line, context=None):
        if context is None:
            context = {}
        res = False
        if line.emergency_costs != 0 \
            and not line.emergency_costs_line_id:
            res = True
        return res

    def generate_emergency_costs_invoice_line(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_line_obj = self.pool.get('account.invoice.line')
        sale_line_obj = self.pool.get('sale.order.line')
        data_obj = self.pool.get('ir.model.data')
        sale_obj = self.pool.get('sale.order')
        value = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.state != 'draft':
                continue
            invoice_lines = invoice.invoice_line
            for invoice_line in invoice_lines:
                for sale_line in invoice_line.sale_lines:
                    if self._emergency_line_to_create(cr, uid,
                                                      sale_line,
                                                      context=context):
                        sale_order = sale_line.order_id
                        model, product_id = data_obj.get_object_reference(
                            cr, uid, 'emergency_costs', 'product_emergency_costs')
                        res = invoice_line_obj.product_id_change(cr, uid, ids, product_id, sale_line.product_uom.id, 
                            qty=0, name='', type='out_invoice', 
                            partner_id=invoice.partner_id.id, fposition_id=invoice.fiscal_position.id, price_unit=sale_line.emergency_costs, 
                            currency_id=False, context=None, company_id=None)
                        value = res.get('value')
                        if value:
                            tax_id = sale_line.tax_id and \
                                [(6, 0, [x.id for x in sale_line.tax_id] or [])]
                            value.update({
                                'invoice_id': invoice.id,
                                'product_id': product_id,
                                'price_unit': sale_line.emergency_costs,
                                'quantity': 1,
                                'invoice_line_tax_id': tax_id,
                                'linked_invoice_line_id': invoice_line.id,
                                'is_emergency_cost_line': True,
                            })
                            uos_id = value.get('product_uos') or value.get('product_uom')
                            if uos_id:
                                value.update({
                                    'uos_id': uos_id,
                                })
                        context.update({'type': 'out_invoice'})
                        new_inv_line_id = invoice_line_obj.\
                            create(cr, uid, value, context=context)
                        sale_line_obj.write(cr, uid,
                            [sale_line.id],
                            {'emergency_costs_line_id' : new_inv_line_id},
                            context=context)
        return True

class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    _columns = {
        'linked_invoice_line_id': fields.many2one('account.invoice.line', 'Linked invoice_line',),
        'is_emergency_cost_line': fields.boolean("Emergency cost line"),
    }

    _defaults = {
        'linked_invoice_line_id': False,
        'is_emergency_cost_line': False,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: