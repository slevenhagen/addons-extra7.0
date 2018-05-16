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
from openerp.osv import osv, fields
from openerp.tools.translate import _

class historical_state(osv.TransientModel):
    _name= 'historical.state'
    _decription = """ This wizard used for changed the state"""
    
    _columns = {
        'historical': fields.selection([('sale_order','Sale Order'),('purchase_order','Purchase Order'),('delivery_order','Delivery Order'),('incoming','Incoming Shipment'),('stock_move','Stock Move')]),
        'sale_ids': fields.many2many('sale.order', 'multi_sale_rel', 'multi_sale_id', 'sale_id', 'Sale Orders'),
        'purchase_ids': fields.many2many('purchase.order', 'multi_purchase_rel', 'multi_purchase_id', 'purchase_id', 'Purchase Orders'),
        'delivery_ids': fields.many2many('stock.picking', 'multi_delivery_rel', 'multi_delivery_id', 'picking_id', 'Delivery Orders', domain=[('type','=','out')]),
        'incoming_ids': fields.many2many('stock.picking', 'multi_incoming_rel', 'multi_incoming_id', 'picking_id', 'Incoming Orders', domain=[('type','=','in')]),
        'move_ids': fields.many2many('stock.move', 'multi_move_rel', 'multi_move_id', 'move_id', 'Moves'),
        'keep_active': fields.boolean('Keep Active'),
        }

    _defaults ={
        'historical':'sale_order'
        }
    
    def historical(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        purchase_obj = self.pool.get('purchase.order')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.historical == 'sale_order':
            change_ids = []
            if not wizard.sale_ids:
                raise osv.except_osv(_('Error!'),_("Please add records."))
            for sale_id in wizard.sale_ids:
                change_ids.append(sale_id.id)
            if not wizard.keep_active:
                cr.execute("UPDATE sale_order SET state='historical', active='False' where id in %s", (tuple(change_ids),))
            else:
                cr.execute("UPDATE sale_order SET state='historical' where id in %s", (tuple(change_ids),))
        elif wizard.historical == 'purchase_order':
            change_ids = []
            if not wizard.purchase_ids:
                raise osv.except_osv(_('Error!'),_("Please add records."))
            for purchase_id in wizard.purchase_ids:
                change_ids.append(purchase_id.id)
            if not wizard.keep_active:
                cr.execute("UPDATE purchase_order SET state='historical', active='False' where id in %s", (tuple(change_ids),))
            else:
                cr.execute("UPDATE purchase_order SET state='historical' where id in %s", (tuple(change_ids),))
        elif wizard.historical == 'delivery_order':
            change_ids = []
            if not wizard.delivery_ids:
                raise osv.except_osv(_('Error!'),_("Please add records."))
            for delivery_id in wizard.delivery_ids:
                change_ids.append(delivery_id.id)
            if not wizard.keep_active:
                cr.execute("UPDATE stock_picking SET state='historical', active='False' where type = 'out' AND id in %s", (tuple(change_ids),))
            else:
                cr.execute("UPDATE stock_picking SET state='historical' where type = 'out' AND id in %s", (tuple(change_ids),))
        elif wizard.historical == 'incoming':
            change_ids = []
            if not wizard.incoming_ids:
                raise osv.except_osv(_('Error!'),_("Please add records."))
            for incoming_id in wizard.incoming_ids:
                change_ids.append(incoming_id.id)
            if not wizard.keep_active:
                cr.execute("UPDATE stock_picking SET state='historical', active='False' where type = 'in' AND id in %s", (tuple(change_ids),))
            else:
                cr.execute("UPDATE stock_picking SET state='historical' where type = 'in' AND id in %s", (tuple(change_ids),))
        elif wizard.historical == 'stock_move':
            change_ids = []
            if not wizard.move_ids:
                raise osv.except_osv(_('Error!'),_("Please add records."))
            for move_id in wizard.move_ids:
                change_ids.append(move_id.id)
            if not wizard.keep_active:
                cr.execute("UPDATE stock_move SET state='historical', active='False' where id in %s", (tuple(change_ids),))
            else:
                cr.execute("UPDATE stock_move SET state='historical' where id in %s", (tuple(change_ids),))
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: