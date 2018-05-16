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
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.addons.product._common import rounding
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class purchase_order(osv.Model):
    _inherit = 'purchase.order'
    
    def _set_minimum_planned_date(self, cr, uid, ids, name, value, arg, context=None):
        if not value: return False
        if type(ids) != type([]):
            ids = [ids]
        # Bad hack to make it work for Web-Client 6.0, as web-client 6.0 has an architectural issue with write operation
        # which calls this method when you change sale order line scheduled date, so just considered Line minimum planned date
        # After this fix Expected date of Sale Order will not be set explicitly
        planned_date = self.minimum_planned_date(cr, uid, ids, name, arg, context)
        for po in self.browse(cr, uid, ids, context=context):
            if planned_date and planned_date.get(po.id):
                 value = planned_date[po.id]
            if po.order_line:
                cr.execute("""update purchase_order_line set
                        date_planned=%s
                    where
                        order_id=%s and
                        (date_planned=%s or date_planned<%s)""", (value, po.id, po.minimum_planned_date, value))
            cr.execute("""update purchase_order set
                    minimum_planned_date=%s where id=%s""", (value, po.id))
        return True

    def minimum_planned_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for purchase in self.browse(cr, uid, ids, context=context):
            res[purchase.id] = False
            if purchase.order_line:
                min_date = purchase.order_line[0].date_planned
                for line in purchase.order_line:
                    if line.date_planned < min_date:
                        min_date = line.date_planned
                res[purchase.id] = min_date
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('historical', 'Historical')
    ]

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
               val1 += line.price_subtotal
               for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id.id, order.partner_id.id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            if res[order.id]['amount_untaxed'] - round(res[order.id]['amount_untaxed'], 2) > 0.00490:
                res[order.id]['amount_untaxed'] = round(res[order.id]['amount_untaxed'], 2) + 0.01
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    _columns = {
        'promise_date' : fields.date('Promised Date'),
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm', help="Incoterm which stands for 'International Commercial terms' implies its a series of sales terms which are used in the commercial transaction."),
        'requester': fields.char('Requester', size=128),
        'active': fields.boolean('Active'),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
        'minimum_planned_date':fields.function(minimum_planned_date, fnct_inv=_set_minimum_planned_date, string='Expected Date', type='date', select=True, help="This is computed as the minimum scheduled date of all purchase order lines' products.",
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['date_planned'], 10),
            }, method=True,
        ),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),
    }
    _defaults = {
        'active':True
        }

    def onchange_partner_id(self, cr, uid, ids, part):
        ret_val = super(purchase_order, self).onchange_partner_id(cr, uid, ids, part)
        ret_val['value'].update({'incoterm_id': False})
        if not part:
            return ret_val
        part = self.pool.get('res.partner').browse(cr, uid, part)
        incoterm_id = part.incoterm.id or False
        if incoterm_id:
            ret_val['value'].update({'incoterm_id': incoterm_id})
        return ret_val

class account_tax(osv.Model):
    _inherit = 'account.tax'

    def compute_inv(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
        Price Unit is a VAT included price

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        res = self._unit_compute_inv(cr, uid, taxes, price_unit, product, partner)
        total = 0.0
        obj_precision = self.pool.get('decimal.precision')
        for r in res:
            prec = obj_precision.precision_get(cr, uid, 'Kpce Price')
            if r.get('balance', False):
                r['amount'] = (r['balance'] * quantity, prec) - total
            else:
                r['amount'] = (r['amount'] * quantity, prec)
                total += r['amount']
        return res
    
    def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
        total = 0.0
        precision_pool = self.pool.get('decimal.precision')
        for r in res:
            if r.get('balance', False):
                r['amount'] = round(r.get('balance', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Kpce Price')) - total
            else:
                r['amount'] = round(r.get('amount', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Kpce Price'))
                total += r['amount']
        return res

    def compute_all(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None):
        res = super(account_tax, self).compute_all(cr, uid, taxes, price_unit, quantity, address_id, product, partner)
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Kpce Price')
        totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        for tax in taxes:
            if tax.price_include:
                tin.append(tax)
            else:
                tex.append(tax)
        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=precision)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty = totalex / quantity
        except:
            pass
        tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=precision)
        for r in tex:
            totalin += r.get('amount', 0.0)
        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
        }

class purchase_order_line(osv.Model):
    _inherit = 'purchase.order.line'

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = super(purchase_order_line, self)._amount_line(cr, uid, ids, prop, arg, context=context)
        return res
    
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}

        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res

        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        #if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        #if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})

        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}

        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id

        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
            uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id})

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.date.context_today(self,cr,uid,context=context)


        supplierinfo = False
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if (qty or 0.0) < min_qty: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})

        # - determine price_unit and taxes_id
        if pricelist_id:
            price = product_pricelist.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order})[pricelist_id]
        else:
            price = product.standard_price
            
        # at end, round price depending of 'Purchase Price' decimal precision
        price_unit_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Kpce Price')
        price = rounding(price, 10 ** -price_unit_precision)

        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})

        return res
    
    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Kpce Price')),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute=dp.get_precision('Kpce Price')),
    }

class account_invoice_line(osv.Model):
    _inherit = 'account.invoice.line'

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = super(account_invoice_line, self)._amount_line(cr, uid, ids, prop, unknow_none, unknow_dict)
        return res

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Kpce Price')),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', type="float",
            digits_compute=dp.get_precision('Kpce Price'), store=True),
    }

class product_template(osv.Model):
    _inherit = 'product.template'
    _columns = {
         'standard_price': fields.float('Cost Price', required=True, digits_compute=dp.get_precision('Kpce Price'), help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),
    }

class product_category(osv.Model):
    _inherit = 'product.category'
    _columns = {
            'active': fields.boolean('Active')
    }

    _defaults = {
	'active': True
    }

class product_product(osv.Model):
    _inherit = 'product.product'
    _columns = {
            'cust_code': fields.char('Customer Ref #', size=128)
    }
    
    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name', '')
            code = d.get('default_code', False)
            supp_code = d.get('supp_code', False)
            if supp_code and supp_code != code:
                name = '[%s] [%s] %s' % (code, supp_code, name)
            elif code:
                name = '[%s] %s' % (code, name)
            if d.get('variants'):
                name = name + ' - %s' % (d['variants'],)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)

        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                              'id': product.id,
                              'name': s.product_name or product.name,
                              'default_code': product.default_code,
                              'variants': product.variants,
                              'supp_code': s.product_code or product.default_code
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': product.name,
                          'default_code': product.default_code,
                          'variants': product.variants,
                          'supp_code': product.default_code
                          }
                result.append(_name_get(mydict))
        return result

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if context is None:
            context = {}
        prod_code = False
        if args:
            procodes = [x[0] for x in args]
            if 'default_code' in procodes and not context.get('skip_prodcode', False):
                prod_code = True
        prod_supp_info = self.pool.get('product.supplierinfo')
        if context.get('pol', False) and context.get('partner_id', False):
            prod_supp_ids = prod_supp_info.search(cr, uid, [('name', '=', context['partner_id'])], context=context)
            IDS = [x.product_id.id for x in prod_supp_info.browse(cr, uid, prod_supp_ids, context=context)]
            args += [('product_tmpl_id.id', 'in', IDS)]
        
        if prod_code:
            new_args = args[:]
            for x in new_args:
                if x[0] == 'default_code':
                    dom1 = x
                    dom2 = ('cust_code', x[1], x[2])
                    prod_supp_ids = prod_supp_info.search(cr, uid, [('product_code', x[1], x[2])], context=context)
                    dom3_ids = [rec.product_id.id for rec in prod_supp_info.browse(cr, uid, prod_supp_ids, context=context)]
                    dom3 = ('product_tmpl_id.id', 'in', dom3_ids)
                    ctx = context.copy()
                    if 'pol' in ctx.keys():
                        del ctx['pol']
                    ctx.update({'skip_prodcode':True})
                    new_IDS = self.search(cr, uid, ['|', dom1, '|', dom2, dom3], context=ctx)
                    args[new_args.index(x)] = ('id', 'in', new_IDS)
                    
        return super(product_product, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
