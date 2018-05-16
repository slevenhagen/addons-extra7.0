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
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    _order = "partner_name, date_due"

    def _set_pay(self, cr, uid, id, name, value, arg, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, id, {'to_pay_handler': value}, context=context)
        return True

    def _get_pay(self, cr, uid, ids, name, args, context=None):
        res = {}
        if context is None:
            context = {}
        total_amt = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.state != 'open':
                res[line.id] = False
            else:
                if line.to_pay_handler:
                    res[line.id] = line.to_pay_handler
                else:
                    res[line.id] = False
        return res

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            cur = invoice.currency_id
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            if res[invoice.id]['amount_untaxed'] - round(res[invoice.id]['amount_untaxed'], 2) > 0.00490:
                res[invoice.id]['amount_untaxed'] = round(res[invoice.id]['amount_untaxed'], 2) + 0.01
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    _columns = {
        'partner_name': fields.related('partner_id', 'name', type='char', readonly=True, size=128, relation='res.partner', store=True, string='Partner'),
        'to_pay': fields.function(_get_pay, fnct_inv=_set_pay, method=True, string="To Pay", type="boolean", store=True),
        'to_pay_handler' : fields.boolean("To Pay"),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all')
    }

    _defaults = {
        'to_pay_handler' : False
    }

    def set_pay_button(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [rec.id], {'to_pay':True})
        return True

    def cancel_pay_button(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [rec.id], {'to_pay':False})
        return True

    def onchange_reference(self, cr, uid, ids, reference, partner_id, context=None):
        supplier_inv_ids = False
        warning = {}
        if reference:
            if not partner_id:
                return {'value':{'reference':False}, 'warning':{'title': 'Warning!', 'message': "Please enter the Supplier first"}}
            supplier_inv_ids = self.search(cr, uid, [('type', '=', 'in_invoice'), ('reference', '=', reference), ('partner_id', '=', partner_id)])
            if supplier_inv_ids:
                warning['title'] = 'Warning !'
                warning['message'] = 'Invoice Reference already exists in the system for this supplier. Please correct it.'
        return {'value':{}, 'warning':warning}

#The following code is in oddello before total_credit = 0.0 in old onchange of partner on voucher
#         if partner_id and not journal_id:
#             partner = partner_pool.browse(cr, uid, partner_id, context=context)
#             if hasattr(partner, 'payment_meth_id') and partner.payment_meth_id:
#                 payment_mode_pool = self.pool.get('payment.mode')
#                 payment_meth = payment_mode_pool.browse(cr, uid, partner.payment_meth_id.id, context=context)
#                 if payment_meth:
#                     default['value']['journal_id'] = payment_meth.journal.id
#                     journal_id = payment_meth.journal.id

#The following code is for choosing move lines
#         if hasattr(partner, 'nat_acc_parent') and partner.nat_acc_parent:
#             partner_ids = partner_pool.search(cr, uid, [('parent_id', 'child_of', [partner_id])], context=context)
#         else:
#             partner_ids = [partner_id]
#
#         DOM = [('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', 'in', partner_ids)]
#         # Search TO PAY first
#
#         PAY_states = 'out_invoice'
#         Credit_States = 'out_refund'
#
#         if ttype == 'payment':
#             PAY_states = 'in_invoice'
#             Credit_States = 'in_refund'
#         if 'multi_pay' in context.keys():
#             inv_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id', 'in', partner_ids), ('type', '=', PAY_states), ('to_pay', '=', 1), ('state', '=', 'open')], context=context)
#             if inv_ids:
#                 DOM += [('invoice', 'in', inv_ids)]
#         ids = move_line_pool.search(cr, uid, DOM, context=context)
#
#         if 'credits' in context.keys():
#             DOM = [('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', 'in', partner_ids)]
#             inv_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id', 'in', partner_ids), ('type', '=', Credit_States), ('state', '=', 'open')], context=context)
#             if inv_ids:
#                 DOM += [('invoice', 'in', inv_ids)]
#             ids += move_line_pool.search(cr, uid, DOM, context=context)
#         ids.reverse()
#         ids = list(set(ids))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
