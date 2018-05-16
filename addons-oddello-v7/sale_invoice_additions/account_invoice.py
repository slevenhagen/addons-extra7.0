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

class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    _columns = {
        'name': fields.char('Description', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'shipping_address_id': fields.many2one('res.partner', 'Shipping Address'),
        'cust_po_num' : fields.char('Cust PO No', size=64),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The partner account used for this invoice."),
    }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        ret_val = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False)
        delivery_addr_id = False
        default_addr_id = False
        opt = [('uid', str(uid))]
        if partner_id:
            opt.insert(0, ('id', partner_id))
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery','default'])
            delivery_addr_id = res['delivery']
            default_addr_id = res['default']
        ret_val['value'].update({'shipping_address_id': default_addr_id})
        if delivery_addr_id:
            ret_val['value'].update({'shipping_address_id': delivery_addr_id})
        return ret_val

class stock_picking(osv.Model):
    _inherit = "stock.picking"

    def action_invoice_create(self, cursor, user, ids, journal_id=False,group=False, type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        sale_obj = self.pool.get('sale.order')
        result = super(stock_picking, self).action_invoice_create(cursor, user,
                ids, journal_id=journal_id, group=group, type=type,
                context=context)
        for rec in self.browse(cursor, user, ids, context=context):
            shiping_id = rec.sale_id and rec.sale_id.partner_shipping_id and rec.sale_id.partner_shipping_id.id or False
            cust_ref = rec.sale_id and rec.sale_id.client_order_ref or ''
            invoice_id = int(result.get(rec.id,0))
            if invoice_id != 0:
                invoice_obj.write(cursor, user, [invoice_id],{'shipping_address_id' : shiping_id, 'cust_po_num' : cust_ref}, context=context)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: