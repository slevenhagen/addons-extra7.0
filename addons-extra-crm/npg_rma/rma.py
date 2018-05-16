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
import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import osv, fields
from openerp import netsvc

class crm_rma(osv.Model):

    def _get_io_ids(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for rma in self.browse(cr, uid , ids, context=context):
            move_ids = []
            res[rma.id] = {
                'incoming_shipping_ids':[],
                'outgoing_shipping_ids':[]
            }
            for line in rma.rma_lines:
                if line.line_incoming_shipment_id:
                    res[rma.id]['incoming_shipping_ids'] += [line.line_incoming_shipment_id.id]
                if line.line_out_shipment_id:
                    res[rma.id]['outgoing_shipping_ids'] += [line.line_out_shipment_id.id]
        return res

    def _get_ids(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for rma in self.browse(cr, uid, ids, context=context):
            move_ids = []
            res[rma.id] = []
            for line in rma.rma_lines:
                if line.requested_procedure in ['repair', 'refurbish']:
                    for move in line.delivery_move_ids:
                        move_ids.append(move.id)
            res[rma.id] = move_ids
        return res


    _name = 'crm.rma'
    _inherit = ['mail.thread']
    _columns = {
        'name' : fields.char('RMA #', size=64, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'partner_address_id': fields.many2one('res.partner', 'Contact Address', readonly=True, states={'draft': [('readonly', False)]}),
        'partner_shipping_id': fields.many2one('res.partner', 'Shipping Address', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'partner_phone': fields.char('Phone', size=16, readonly=True, states={'draft': [('readonly', False)]}),
        'email_from': fields.char('Email', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]}),
        'date_create' : fields.datetime('Creation Date', readonly=True, states={'draft': [('readonly', False)]}),
        'date_received' : fields.datetime('Received Date', readonly=True, states={'draft': [('readonly', False)]}),
        'note' : fields.text('Notes', size=256),
        'id' : fields.integer('ID'),
        'priority' : fields.selection([('lowest', 'Lowest'), ('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('highest', 'Highest')], 'Priority', readonly=True, states={'draft': [('readonly', False)]}),
        'ref': fields.reference('Reference', selection=[('res.partner', 'Partner'), ('calendar.event', 'Event'), ('product.product', 'Product'), ('account.invoice', 'Invoice'), ('crm.meeting', 'Meeting'), ('stock.production.lot', 'Production Lot'), ('purchase.order', 'Purchase Order'), ('account.voucher', 'Voucher'), ('sale.order', 'Sales Order'), ('project.project', 'Project'), ('project.task', 'Project Task')], size=128, readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Responsible',),
        'cause' : fields.text('Issues Found', size=256,),
        # 'product_id': fields.many2one('product.product','Product', readonly=True, states={'draft': [('readonly', False)]}),
        'state' : fields.selection([('draft', 'Draft'), ('open', 'Open'), ('in_progress', 'In Progress'), ('pending', 'Pending'), ('done', 'Done'), ('cancel', 'Cancelled'), ('repaired', 'Repaired')], 'State', readonly=True),
        'requested_procedure' : fields.selection([('repair', 'Repair'), ('refurbish', 'Refurbish'), ('exchange', 'Exchange'), ('credit', 'Credit')], 'Requested Procedure', readonly=True, states={'draft': [('readonly', False)]}, required=True),
        'cust_comments' : fields.text('Customer Comments', size=256),
        'email_cc' : fields.text('Watchers Emails', size=256,),
        'message_ids':fields.one2many('crm.rma.message', 'rma_id', 'Messages', readonly=True, states={'draft': [('readonly', False)]}),
        'product_lot_id' :   fields.many2one('stock.production.lot', 'Lot Number'),
        'rma_lines' : fields.one2many('crm.rma.line', 'rma_id', 'Lines', readonly=True, states={'draft': [('readonly', False)]}),

        'incoming_shipment_id':fields.many2one('stock.picking', 'Incoming move'),
        'incoming_move_ids': fields.related('incoming_shipment_id','move_lines', type='one2many', relation='stock.move', string='Incoming move lines', readonly=True),
        'out_shipment_id':fields.many2one('stock.picking', 'Outgoing move'),
        'out_move_ids':fields.related('out_shipment_id','move_lines', type='one2many', relation='stock.move', string='Outgoing move lines', readonly=True),

        'delivery_id':fields.related('rma_lines', 'delivery_id', type='many2one', relation='stock.picking', string='Delivery Order', readonly=True),
        'delivery_move_ids':fields.function(_get_ids, method=True, type='one2many', obj='stock.move', string='Delivery Order'),
        # 'date_processed' : fields.datetime('Processed Date', readonly=True, states={'draft': [('readonly', False)]}),
        'write_date' : fields.datetime('Updated Date', readonly=True),
        'write_uid': fields.many2one('res.users', 'Last Update by', readonly=True),
        'date_hold' : fields.datetime('Holding Date', readonly=True, states={'draft': [('readonly', False)]}),
        'date_analyze' : fields.datetime('Analyzed Date', readonly=True, states={'draft': [('readonly', False)]}),
        'claim_id': fields.many2one('crm.claim', 'Claim ID'),
        'incoming_shipping_ids':fields.function(_get_io_ids, method=True, type='many2many', obj='stock.picking', string='Pickings', multi='all'),
        'outgoing_shipping_ids':fields.function(_get_io_ids, method=True, type='many2many', obj='stock.picking', string='Delivery Orders', multi='all'),
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value': {'partner_address_id': False, 'partner_shipping_id': False, 'email_from':'', 'partner_phone':''}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery', 'contact'])
        contact_address = addr.get('contact', False) and self.pool.get('res.partner').browse(cr, uid, addr['contact'])
        val = {
            'partner_address_id': addr.get('contact', False),
            'partner_shipping_id': addr.get('delivery', False),
            'email_from': contact_address and contact_address.email,
            'partner_phone': contact_address and contact_address.phone
        }
        return {'value': val}

    def _get_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.company').search(cr, uid, [])
        if len(company_id) == 1:
            return company_id[0]
        else:
            return False

    def action_approve(self, cr, uid, ids, context={}):
        warehouse_obj = self.pool.get('stock.warehouse')
        for rma in  self.browse(cr, uid, ids, context=context):
            if not rma.rma_lines:
                continue
            if rma.company_id:
                warehouse_ids = warehouse_obj.search(cr, uid, [('company_id', '=', rma.company_id.id)])
            else:
                warehouse_ids = warehouse_obj.search(cr, uid, [])
            if not warehouse_ids :
                continue
            warehouse = warehouse_obj.browse(cr, uid, warehouse_ids[0], context=context)
            rma_number = self.pool.get('ir.sequence').get(cr, uid, 'crm.rma')
            rma_vals = {'state':'in_progress',
                        'name': rma_number,
                        }

            for line in rma.rma_lines:
                requested_procedure = line.requested_procedure

                if requested_procedure == 'exchange':
                    picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                                'origin' : rma_number + (line.name and (': ' + line.name) or ''),
                                                'type' : 'out',
                                                'move_lines' : [],
                                                'partner_id': rma.partner_id.id,
                                                'address_id' : rma.partner_shipping_id and rma.partner_shipping_id.id
                                                }, context=context)
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                                                 'name' : rma_number + (line.name and (': ' + line.name) or ''),
                                                 'product_id':line.product_id and line.product_id.id,
                                                 'product_qty': line.product_qty,
                                                 'location_id' : warehouse.lot_stock_id.id,
                                                 'location_dest_id' : rma.partner_id.property_stock_customer.id,
                                                 'product_uom' : line.product_uom and line.product_uom.id,
                                                 'picking_id' : picking_id
                                                 })
                    line.write({'line_out_shipment_id' : picking_id})


                pick_id = self.pool.get('stock.picking').create(cr, uid, {
                                            'origin' : rma_number + (line.name and (': ' + line.name) or ''),
                                            'type' : 'in',
                                            'move_lines' : [],
                                            'address_id' : rma.partner_shipping_id and rma.partner_shipping_id.id,
                                            'invoice_state':'2binvoiced'
                                            }, context=context)
                move_ids = []
                move_id = self.pool.get('stock.move').create(cr, uid, {
                                                 'name' : rma_number + (line.name and (': ' + line.name) or ''),
                                                 'product_id':line.product_id and line.product_id.id,
                                                 'product_qty': line.product_qty,
                                                 'location_id' : rma.partner_id.property_stock_customer.id,
                                                 'location_dest_id' : warehouse.lot_return_id.id,
                                                 'product_uom' : line.product_uom and line.product_uom.id,
                                                 'picking_id' : pick_id,
                                                 'prodlot_id': line.product_lot_id and line.product_lot_id.id  # Pass the lot id reference to the move
                                                 })
                move_ids.append(move_id)
                line.write({'line_incoming_shipment_id' : pick_id, 'incoming_move_id':move_id})

                if requested_procedure == 'credit':
                    picking_pool = self.pool.get('stock.picking')
                    context['inv_type'] = '2binvoiced'
                    journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale_refund')]) and self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale_refund')])[0] or False
                    picking_pool.action_invoice_create(cr, uid, [pick_id], journal_id=journal_id,
                        group=False, type=None, context=context)

                self.pool.get('stock.move').action_confirm(cr, uid, move_ids)
                self.pool.get('stock.move').force_assign(cr, uid, move_ids)
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_confirm', cr)

            self.write(cr, uid, [rma.id], rma_vals, context=context)
        return True


    def rma_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'cancel'}, context=context)
        return True

    def rma_draft(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True

    def rma_done(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        states = vals.get('state', False)
        if states and states in ['cancel', 'draft']:
            return super(crm_rma, self).write(cr, uid, ids, vals, context)
        for rma in self.browse(cr, uid, ids):
            line_counter = len([l for l in rma.rma_lines if l.requested_procedure in ['repair', 'refurbish']])
            repaired_counter = 0
            done = 0
            for line in rma.rma_lines:
                if line.requested_procedure in ['repair', 'refurbish']:
                    repaired = line.repaired
                    if repaired:
                        repaired_counter += 1
                        picking_state = line.repair_id and line.repair_id.picking_id and line.repair_id.picking_id.state or ' '
                        if picking_state == 'done':
                            done += 1
            if line_counter == repaired_counter:
                vals['state'] = 'repaired'
                if line_counter == done:
                    vals['state'] = 'done'
        return super(crm_rma, self).write(cr, uid, ids, vals, context)


    _defaults = {
        'priority':'normal',
        'user_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
        'company_id':lambda self, cr, uid, c: self._get_company(cr, uid, context=c),
        'requested_procedure': 'exchange',
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'name': False})
        rma = self.browse(cr, uid, id, context=context)
        for line in rma.rma_lines:
            self.pool.get('crm.rma.line').write(cr, uid, [line.id], {'line_incoming_shipment_id': False, 'line_out_shipment_id': False,
                                                                     'repair_id': False, 'incoming_move_id': False})
        return super(crm_rma, self).copy(cr, uid, id, default, context)

class  crm_rma_line(osv.Model):
    _name = 'crm.rma.line'
    _description = "RMA Lines"
    _columns = {
        'name' : fields.char('Description' , size=64),
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'product_lot_id' : fields.many2one('stock.production.lot', 'Lot Number'),
        'rma_id' : fields.many2one('crm.rma', 'RMA'),
        'product_qty': fields.float('Quantity (UoM)', digits=(16, 2), required=True),
        'incoming_move_id': fields.many2one('stock.move', string='Incoming move', readonly=True),
        'in_state': fields.related('incoming_move_id', 'state', type='char', string='Incoming move state', readonly=True),
        'repair_id': fields.many2one('mrp.repair', string='Repair Order', readonly=True),
        'repaired': fields.related('repair_id', 'repaired', type='boolean', string='Repaired', readonly=True),
        'delivery_id':fields.related('repair_id', 'picking_id', type='many2one', relation='stock.picking', string='Delivery Order', readonly=True),
        'delivery_move_ids':fields.related('delivery_id', 'move_lines', type='one2many', relation='stock.move', string='Delivery Order', readonly=True),
        'requested_procedure' : fields.selection([('repair', 'Repair'), ('refurbish', 'Refurbish'), ('exchange', 'Exchange'), ('credit', 'Credit')], 'Requested Procedure', required=True),
        'line_incoming_shipment_id':fields.many2one('stock.picking', 'Incoming Picking'),
        'line_out_shipment_id':fields.many2one('stock.picking', 'Outgoing Picking'),
        'guarantee_limit': fields.date('Guarantee limit', readonly=True, help="The guarantee limit is computed as: last move date + warranty stamped on the last move."),
    }

    _defaults = {
        'product_qty': lambda *a: 1,
    }
    
    def rma_line_make_repair(self, cr, uid, ids, context={}):
        repair_obj = self.pool.get('mrp.repair')
        for line in self.browse(cr, uid, ids, context=context):
            vals = {
                'product_id': line.product_id.id,
                'partner_id' : line.rma_id.partner_id.id,
                'address_id': line.rma_id.partner_shipping_id.id,
                'prodlot_id': line.product_lot_id and line.product_lot_id.id,
                'location_id': line.incoming_move_id.location_dest_id and line.incoming_move_id.location_dest_id.id,
                'location_dest_id': line.rma_id.partner_id.property_stock_customer.id,
                'move_id': line.incoming_move_id.id,
            }
            new_vals = repair_obj.onchange_partner_id(cr, uid, [], line.rma_id.partner_id.id, line.rma_id.partner_shipping_id.id)
            vals.update(new_vals['value'])
            repair_id = repair_obj.create(cr, uid, vals, context=context)
            line.write({"repair_id":repair_id})
        return True

    def onchange_product(self, cr, uid, ids, prod):
        if not prod:
            return {'value': {'product_uom': False, 'name': ''}}
        prod_obj = self.pool.get('product.product').browse(cr, uid, prod)
        uom = prod_obj.uom_id and prod_obj.uom_id.id or False
        name = prod_obj.name
        return {'value': {'product_uom': uom, 'name': name}}

    def get_lst_move_and_limit_from_production_lot(self, cr, uid, lot):
        """
        Return the last sale move which is a move from Stock Location to Customers Location and calculate
        the guarantee limit based on the the computation:
        Guarantee Limit = The date the product was sent to customer + warranty timestamped on the the move
        Following 3 scenarios are taken care of:
        1) A product may have been returned to the customer twice after repairing it twice. In this case, the date the product first moved out of the warehouse should be considered in calculation.

        2) A product may have been returned back to NUVICO for restocking purpose.

        3) A product may have been exchanged with another product.
        """

        move_obj = self.pool.get('stock.move')
        lst_move = False
        limit = False
        move_ids = move_obj.search(cr, uid, [('prodlot_id', '=', lot.id), ('move_from_sales', '=', True), ('state', '=', 'done')], order='date desc')
        if move_ids:
            lst_move = move_obj.browse(cr, uid, move_ids[0])
            limit = datetime.datetime.strptime(lst_move.date, '%Y-%m-%d %H:%M:%S') + \
                                                relativedelta(months=int(lst_move.warranty))
        return (lst_move, limit)

    def onchange_lot(self, cr, uid, ids, lot_id):
        move_obj = self.pool.get('stock.move')
        production_lot_obj = self.pool.get('stock.production.lot')
        res = {'value': {}}
        if lot_id:
            lot = production_lot_obj.browse(cr, uid, lot_id)
            limit = self.get_lst_move_and_limit_from_production_lot(cr, uid, lot)[1]
            res['value'] = {'guarantee_limit': limit and limit.strftime('%Y-%m-%d'),
                            'product_id': lot.product_id.id,
                            'product_uom': lot.product_id.uom_id.id,
                            'name': lot.product_id.name
                            }
        return res
    
    
    def create(self, cr, uid, vals, context=None):
        production_lot_obj = self.pool.get('stock.production.lot')
        if vals.has_key('product_lot_id') and vals['product_lot_id']:
            lot = production_lot_obj.browse(cr, uid, vals['product_lot_id'])
            limit = self.get_lst_move_and_limit_from_production_lot(cr, uid, lot)[1]
            vals['guarantee_limit']=limit and limit.strftime('%Y-%m-%d')
        return super(crm_rma_line, self).create(cr, uid, vals, context=context)
 
    def write(self, cr, uid,ids, vals, context=None):
        production_lot_obj = self.pool.get('stock.production.lot')
        if vals.has_key('product_lot_id') and vals['product_lot_id']:
            lot = production_lot_obj.browse(cr, uid, vals['product_lot_id'])
            limit = self.get_lst_move_and_limit_from_production_lot(cr, uid, lot)[1]
            vals['guarantee_limit']=limit and limit.strftime('%Y-%m-%d')
            
        return super(crm_rma_line, self).write(cr, uid,ids, vals, context=context)

class crm_rma_message(osv.Model):
    _name = 'crm.rma.message'
    _description = 'Message'
    _columns = {
        'name':fields.text('Message', size=240),
        'rma_id': fields.many2one('crm.rma', 'RMA'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
