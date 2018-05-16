#-*- coding: utf-8 -*-
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

from openerp.osv import osv,fields
import openerp.addons.decimal_precision as dp
from openerp.addons.product._common import rounding
from openerp.tools.translate import _
from openerp import netsvc
import time

class sale_order(osv.Model):
    _inherit = 'sale.order'
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
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
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            if res[order.id]['amount_untaxed'] - round(res[order.id]['amount_untaxed'], 2) > 0.00490:
                res[order.id]['amount_untaxed'] = round(res[order.id]['amount_untaxed'], 2) + 0.01
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    _columns = {
        'promise_date' : fields.date('Promised Date'),
        'truck_load_number' : fields.char('Truck Load Number', size=64),
        'third_party_bill_to_id': fields.many2one('res.partner', '3rd Party Freight Charges Bill to'),
        'active': fields.boolean('Active'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('historical','Historical')
            ], 'Order State', readonly=True, help="Gives the state of the quotation or sales order. \nThe exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception). \nThe 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the date 'Ordered Date'.", select=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Untaxed Amount',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Taxes',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'), string='Total',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
    }

    _defaults ={
        'active':True
        }
    
    def onchange_partner_id(self, cr, uid, ids, part,context=None):
        ret_val = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        ret_val['value'].update({'incoterm': False})
        if not part:
            return ret_val
        part = self.pool.get('res.partner').browse(cr, uid, part)
        incoterm_id = part.incoterm_sale_id.id or False
        if incoterm_id:
            ret_val['value'].update({'incoterm': incoterm_id})
        return ret_val

class stock_picking(osv.Model):
    _inherit = 'stock.picking'
    _columns = {
        'promise_date' : fields.related("sale_id", "promise_date", type="date", string="Promised Date"),
        'client_order_ref' : fields.related("sale_id", "client_order_ref", type="char", string="Customer Reference"),
        'truck_load_number' : fields.char('Truck Load Number', size=64),
    }

class stock_picking_out(osv.Model):
    _inherit = 'stock.picking.out'
    _columns = {
        'promise_date' : fields.related("sale_id", "promise_date", type="date", string="Promised Date"),
        'client_order_ref' : fields.related("sale_id", "client_order_ref", type="char", string="Customer Reference"),
        'truck_load_number' : fields.char('Truck Load Number', size=64),
    }

class product_template(osv.Model):
    _inherit = 'product.template'
    _columns = {
         'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Kpce Price'), help="Base price for computing the customer price. Sometimes called the catalog price."),
    }

class sale_order_line(osv.Model):
    _inherit ='sale.order.line'
    
    def _weight_net(self, cr, uid, ids, field_name, arg, context=None):
        """Compute the net weight of the given Sale Order Lines."""
        result = {}
        
        uom_obj = self.pool.get('product.uom')
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = 0.0
            if line.product_id and line.product_id.weight_net > 0.00:
                qty = line.product_uom_qty
                # Convert the qty to the right unit of measure
                if line.product_uom.id <> line.product_id.uom_id.id:
                    qty = uom_obj._compute_qty(cr, uid, line.product_uom.id,
                                               line.product_uom_qty,
                                               line.product_id.uom_id.id)
                weight = qty * line.product_id.weight_net
                result[line.id] = weight
        return result
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = super(sale_order_line, self)._amount_line(cr, uid, ids, field_name, arg, context=context)
        return res

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context=None):
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined !'), _('You have to select a customer in the sales form !\nPlease set one customer before choosing a product.'))
        warning = {}
        warning_msgs = []
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        if partner_id:
            partner_lang = partner_obj.browse(cr, uid, partner_id).lang
        context = {'lang': lang, 'partner_id': partner_id}
        context_partner = {'lang': partner_lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0, 'product_packaging': False,
                'product_uos_qty': qty, 'tax_id':[]}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime('%Y-%m-%d')

        result = {}
        product_obj = product_obj.browse(cr, uid, product, context=context)
        if not packaging and product_obj.packaging:
            packaging = product_obj.packaging[0].id
            result['product_packaging'] = packaging

        if packaging:
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            pack = self.pool.get('product.packaging').browse(cr, uid, packaging, context=context)
            q = product_uom_obj._compute_qty(cr, uid, uom, pack.qty, default_uom)
#            qty = qty - qty % q + q
            if qty and (q and not (qty % q) == 0):
                ean = pack.ean or _('(n/a)')
                qty_pack = pack.qty
                type_ul = pack.hu_type_id
                warn_msg = _("You selected a quantity of %d Units.\n"
                            "But it's not compatible with the selected packaging.\n"
                            "Here is a proposition of quantities according to the packaging:\n\n"
                            "EAN: %s Quantity: %s Type of HU Type: %s") % \
                                (qty, ean, qty_pack, type_ul.name)
                warning_msgs.append('%s :\n%s' % (_('Picking Information !'), warn_msg))
            result['product_uom_qty'] = qty

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
#         if product_obj.description_sale:
#             result['notes'] = product_obj.description_sale
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['delay'] = (product_obj.sale_delay or 0.0)
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
            result.update({'type': product_obj.procure_method})

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}

        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        if (product_obj.type=='product') and (product_obj.virtual_available * uom2.factor < qty * product_obj.uom_id.factor) \
          and (product_obj.procure_method=='make_to_stock'):
            warn_msg = _('You plan to sell %.2f %s but you only have %.2f %s available !\nThe real stock is %.2f %s. (without reservations)') % \
                    (qty, uom2 and uom2.name or product_obj.uom_id.name,
                     max(0,product_obj.virtual_available), product_obj.uom_id.name,
                     max(0,product_obj.qty_available), product_obj.uom_id.name)
            warning_msgs.append('%s :\n%s' % (_('Not enough stock !'), warn_msg))

        # get unit price
        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                         'Please set one before choosing a product.')
            warning_msgs.append('%s :\n%s' % (_('No Pricelist !'), warn_msg))
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom,
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Couldn't find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")
                warning_msgs.append('%s :\n%s' % (_('No valid pricelist line found !'), warn_msg))
            else:
                # at end, round price depending of 'Sale Unit' decimal precision
                price_unit_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Kpce Price')
                price = rounding(price, 10**-price_unit_precision)
                result.update({'price_unit': price})

        if warning_msgs:
            warning = {
                'title': _('Configuration Error !'),
                'message' : '\n\n'.join(warning_msgs)
            }
        return {'value': result, 'domain': domain, 'warning': warning}

    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Kpce Price')),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Kpce Price')),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True, states={'draft': [('readonly', False)]}, help="The analytic account related to a sales order line."),
        'weight_net': fields.function(_weight_net, method=True, string='Net Weight', help="The net weight in Kg.",
            store={
                # Low priority to compute this before fields in other modules
               'sale.order.line': (lambda self, cr, uid, ids, context=None: ids,
                   ['product_uom_qty', 'product_uom', 'product_id'], -13),
            },
        ),
    }
    
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('procurement.order').quantity_get(cr, uid,
                        line.procurement_id.id, context=context)

        def _get_line_uom(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('procurement.order').uom_get(cr, uid,
                        line.procurement_id.id, context=context)

        create_ids = []
        sales = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.invoiced:
                if line.product_id:
                    a = line.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = line.product_id.categ_id.property_account_income_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'),
                                _('There is no income account defined ' \
                                        'for this product: "%s" (id:%d)') % \
                                        (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    a = prop and prop.id or False
                uosqty = _get_line_qty(line)
                uos_id = _get_line_uom(line)
                pu = 0.0
                if uosqty:
                    pu = round(line.price_unit * line.product_uom_qty / uosqty,
                            self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
                fpos = line.order_id.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                if not a:
                    raise osv.except_osv(_('Error !'),
                                _('There is no income category account defined in default Properties for Product Category or Fiscal Position is not defined !'))
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'origin': line.order_id.name,
                    'account_id': a,
                    'price_unit': pu,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
#                     'note': line.notes,
                    'account_analytic_id': line.analytic_account_id and line.analytic_account_id.id or False,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced': True})
                sales[line.order_id.id] = True
                create_ids.append(inv_id)
        # Trigger workflow events
        wf_service = netsvc.LocalService("workflow")
        for sid in sales.keys():
            wf_service.trg_write(uid, 'sale.order', sid, cr)
        return create_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: