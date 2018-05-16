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

class Invoice(osv.Model):
    _inherit = 'account.invoice'
    _columns = {
        'user_id': fields.many2one('res.users', 'User', readonly=True, track_visibility='onchange', states={'draft':[('readonly',False)]}),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(Invoice, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context.get('type') == 'out_invoice':
            if res.get('toolbar'):
                temp = res['toolbar']['relate']
                res.get('toolbar').update({'relate' : []})
                for rec in temp:
                    if rec['name'] != 'BOL':
                        continue
                    else:
                        rec['name'] = rec['string'] = 'BOL'
                        res.get('toolbar').update({'relate' : [rec]})
        return res

class Attachment(osv.Model):
    _inherit = 'ir.attachment'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        picking_obj = self.pool.get('stock.picking.out')
        sale_obj = self.pool.get('sale.order')
        flag = False
        if context.get('active_model','') == 'account.invoice' and context.get('active_id', False):
            if context.get('type') == 'out_invoice':
                picking_ids = picking_obj.search(cr, uid, [('invoice_id', '=', context.get('active_id', False))], context=context)
                if picking_ids:
                    sale_ids = sale_obj.search(cr, uid, [('picking_ids', 'in', picking_ids)], context=context)
                    if sale_ids:
                        args.extend([('res_model','=','sale.order'),('res_id','=',sale_ids[0])])
                        flag = True
            else:
                picking_ids = picking_obj.search(cr, uid, [('invoice_id', '=', context.get('active_id', False))], context=context)
                if picking_ids:
                    sale_ids = sale_obj.search(cr, uid, [('picking_ids', 'in', picking_ids)], context=context)
                    args.extend([('res_model','=','stock.picking.out'),('res_id','=',picking_ids[0])])

        elif context.get('active_model','') == 'stock.picking.out' or context.get('sale_order_att'):
            if context.get('mbol_att',False):
                atts_id = picking_obj.browse(cr, uid, context.get('active_id', False), context=context).attached_mbol_report_id.id
                args.extend([('id', '=', atts_id)])
            else:
                if context.get('active_id', False):
                    sale_ids = sale_obj.search(cr, uid, [('picking_ids', 'in', [context.get('active_id', False)])], context=context)
                    if sale_ids:
                        args.extend([('res_model','=','sale.order'),('res_id','=',sale_ids[0])])
                        flag = True
        if not flag:
            if context.get('active_model','') and context.get('active_model','')!= 'ir.ui.menu':
#                args.extend([('res_model','=',context.get('active_model','')),(('res_id','=',context.get('active_id', False)))])
                return super(Attachment, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        return super(Attachment, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
