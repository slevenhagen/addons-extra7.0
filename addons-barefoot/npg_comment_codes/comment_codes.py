# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPoint Group INC (<http://www.novapointgroup.com>)
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

class npg_comment_codes(osv.osv):
    _name = "npg.comment.codes"
    _description = "Comment codes"
    _columns = {
        'name': fields.char('Comment', size=512, translate=True, required=True),
        'code': fields.char('Code', size=64, translate=True),
        'desc':fields.text('Description'),
    }
    _order = "name"
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + '--'+name
            res.append((record['id'], name))
        return res
    

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
               # 'comment_code':fields.many2one('npg.comment.codes', "Comment Code"),
               'comment_code':fields.many2one('npg.comment.codes', 'Comment Code'),
                }
    

class sale(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
                'comment_code':fields.many2one('npg.comment.codes', "FOB Terms")
                }
    
    def action_invoice_create(self, cr, uid, ids, context=None):
        inv_id = super(sale, self).action_invoice_create(cr, uid, ids, context)
        for so in self.browse(cr,uid,ids,context):
            if so.comment_code:
                self.pool.get('account.invoice').write(cr,uid,inv_id,{'comment_code':so.comment_code.id})
        return inv_id

class purchase(osv.osv):
    _inherit = "purchase.order"
    
    _columns =  {
                'comment_code':fields.many2one('npg.comment.codes', "FOB Terms")
                }
    def action_invoice_create(self, cr, uid, ids, context=None):
        inv_id = super(purchase, self).action_invoice_create(cr, uid, ids, context)
        for po in self.browse(cr,uid,ids,context):
            if po.comment_code:
                self.pool.get('account.invoice').write(cr,uid,inv_id,{'comment_code':po.comment_code.id})
        return inv_id



