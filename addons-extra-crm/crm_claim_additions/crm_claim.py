# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
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
from openerp.tools.translate import _

class crm_claim_problem(osv.Model):
    """
    This Model is defining the problems relevant to the different categories.
    
    """
    _name = 'crm.claim.problem'
    _description = 'Problems in the Products to Claim'
    
    _columns = {
        'name': fields.char('Problem Description', size=64, required=True),
        'prod_categ_id': fields.many2one('product.category', 'Product Category'),
        'details': fields.text('Details')
    }

class crm_claim(osv.Model):
    """
    This model is inherited from the CRM Claim and adds a tab to the claim for the product information relevant to claim.
    """
    _inherit = 'crm.claim'
    
    _columns = {
        'product_info_ids': fields.one2many('crm.product.info', 'claim_id', 'Product Information'),
        'claim_number':fields.char('Claim Number',readonly=True,size=32),
        'dealer_id': fields.related('partner_id', 'dealer_id',type='char', string='Dealer ID', size=32),
    }
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('claim_number', False):
            vals['claim_number'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.claim.advance')
        return super(crm_claim, self).create(cr, uid, vals, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'claim_number': self.pool.get('ir.sequence').get(cr, uid, 'crm.claim.advance'),
        })
        return super(crm_claim, self).copy(cr, uid, id, default, context=context)

    def onchange_dealer_id(self, cr, uid, ids, dealer, context=None):
        partner_details = {'value': {
                    'partner_address_id': False,
                    'email_from': False, 
                    'partner_phone': False,
                    'partner_mobile': False,
                    'partner_id' : False
                    }}
        if not dealer:
            return partner_details
        add_obj = self.pool.get('res.partner')
        add_ids = add_obj.search(cr, uid, [('dealer_id','=',dealer)], context=context, limit=1)
        if not add_ids:
            return partner_details
        for add_rec in add_obj.browse(cr, uid, add_ids, context=context):
            partner_details = self.onchange_partner_id(cr, uid, ids, add_rec.parent_id.id, email=False)
            partner_details['value']['partner_id'] = add_rec.parent_id.id
        return partner_details

class crm_product_info(osv.Model):
    """
    This model is used to describe the information related to the product which is relevant to the claim.
    """
    _name = 'crm.product.info'
    _description = ' Product Information for Claims'
    
    _rec_name = 'product_id'
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'prod_lot_id': fields.many2one('stock.production.lot', 'Production Lot'),
        'prod_categ_id': fields.many2one('product.category', 'Product Category'),
        'problem_id': fields.many2one('crm.claim.problem', 'Claim Problem'),
        'claim_id': fields.many2one('crm.claim', 'Claim', ondelete="set null")
    }

    def onchange_product_prodlot(self, cr, uid, ids, prod_lot_id, product_id=False):
        res = {}
        if prod_lot_id:
            prod_lot_rec = self.pool.get('stock.production.lot').browse(cr, uid, prod_lot_id)
            if product_id and prod_lot_rec.product_id != product_id:
                raise osv.except_osv(_('User Error!'),_('Kindly Choose the Production lot of the same product!'))
            res.update({'value':{'product_id':prod_lot_rec.product_id.id, 'prod_categ_id':prod_lot_rec.product_id.categ_id.id}})        
        elif product_id:
            product_rec = self.pool.get('product.product').browse(cr,uid,product_id)
            res.update({'value':{'prod_categ_id':product_rec.categ_id.id}})
        return res

    def onchange_prod_categ(self, cr, uid, ids, prod_categ_id, product_id):
        res = {}
        if prod_categ_id and product_id:
            product_rec = self.pool.get('product.product').browse(cr, uid, product_id)
            if product_rec.categ_id.id != prod_categ_id:
                raise osv.except_osv(_('User Error!'),_('Kindly Choose the Category which matches with the chosen product!'))
        return res


class res_partner(osv.Model):
    _inherit = 'res.partner'

    _columns = {
            'dealer_id': fields.char('Dealer ID', size=32),
    }
    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','zip','country_id', 'city','partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                addr = r['name'] or ''
                if r['name'] and (r['city'] or r['country_id']):
                    addr += ', '
                addr += (r['country_id'] and r['country_id'][1] or '') + ' ' + (r['city'] or '') + ' '  + (r['street'] or '')
                if (context.get('contact_display', 'contact')=='partner_id') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr.strip() or '/')))
                else:
                    res.append((r['id'], addr.strip() or '/'))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: