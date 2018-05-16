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
import report
from openerp.report import report_sxw
import StringIO
import cStringIO
import base64
import datetime
import time
import logging
import pooler
from openerp.osv.fields import function as function_class
import pyPdf
import netsvc
from openerp import netsvc

def create_source_pdf(self, cr, uid, ids, data, report_xml, context=None):
    if not context:
        context={}
    pool = pooler.get_pool(cr.dbname)
    pool_attach = pool.get('ir.attachment')
    picking_obj = pool.get('stock.picking.out')
    myflag = False

#     if data['model'] == 'stock.picking.out':
    if context['active_model'] == 'stock.picking.out':
        if report_xml.name in ['Bill of Lading', 'Master Bill of Lading']:
            myflag = True
    attach = report_xml.attachment
    singleton = False
    MBOL = []
    M_attach = False
    if attach:
        objs = self.getObjects(cr, uid, ids, context)
        results = []
        for obj in objs:
            aname = eval(attach, {'object':obj, 'time':time})
            result = False
            if not myflag:
                if report_xml.attachment_use and aname and context.get('attachment_use', True):
                    aids = pool_attach.search(cr, uid, [('datas_fname','=',aname+'.pdf'),('res_model','=',self.table),('res_id','=',obj.id)])
                    if aids:
                        brow_rec = pool_attach.browse(cr, uid, aids[0])
                        if not brow_rec.datas:
                            continue
                        d = base64.decodestring(brow_rec.datas)
                        results.append((d,'pdf'))
                        continue
            if myflag and report_xml.name == 'Master Bill of Lading':
                data.update({'objects' : objs})

            if not MBOL:
                result = self.create_single_pdf(cr, uid, [obj.id], data, report_xml, context)
            else:
                result = MBOL

#             if data['model'] == 'stock.picking.out' and report_xml.name == 'Master Bill of Lading':
            if context['active_model'] == 'stock.picking.out' and report_xml.name == 'Master Bill of Lading':
                MBOL = result
                singleton = True

            if not result:
                return False
            if aname:
                try:
                    name = aname+'.'+result[1]
                    if myflag:
                        if report_xml.name == 'Master Bill of Lading':
                            att_id = picking_obj.browse(cr, uid, obj.id).attached_mbol_report_id.id
                            if att_id:
                                pool_attach.unlink(cr, uid, [att_id])
                            aname = 'Master BOL-'+ time.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            #unlink the previous attached BOL report
                            att_id = picking_obj.browse(cr, uid, obj.id).attached_report_id.id
                            if att_id:
                                pool_attach.unlink(cr, uid, [att_id])
                            aname = 'BOL-'+ time.strftime('%Y-%m-%d %H:%M:%S')
                    if not M_attach:
                       new_attach = pool_attach.create(cr, uid, {
                        'name': aname,
                        'datas': base64.encodestring(result[0]),
                        'datas_fname': name,
                        'res_model': self.table,
                        'res_id': obj.id,
                        }, context=context
                    )
                    else:
                        new_attach = M_attach
                    if myflag:
                        # Create new attachment of BOL report
                        new_val = {'attached_report_id':new_attach}
                        if report_xml.name == 'Master Bill of Lading':
                            M_attach = new_attach
                            new_val = {'attached_mbol_report_id':new_attach}
                        picking_obj.write(cr, uid, obj.id, new_val)
                except Exception:
                    #TODO: should probably raise a proper osv_except instead, shouldn't we? see LP bug #325632
                    logging.getLogger('report').error('Could not create saved report attachment', exc_info=True)
            if not MBOL:
                results.append(result)
        if results:
            if results[0][1]=='pdf':
                from pyPdf import PdfFileWriter, PdfFileReader
                output = PdfFileWriter()
                for r in results:
                    reader = PdfFileReader(cStringIO.StringIO(r[0]))
                    for page in range(reader.getNumPages()):
                        output.addPage(reader.getPage(page))
                s = cStringIO.StringIO()
                output.write(s)
                return s.getvalue(), results[0][1]
    return self.create_single_pdf(cr, uid, ids, data, report_xml, context)

report_sxw.report_sxw.create_source_pdf = create_source_pdf

class stock_picking(osv.Model):

    _inherit = 'stock.picking'

    def _get_full_name(self, cr, uid, ids, field, arg, context=None):
        return {}

    def _search_orders(self, cr, uid, obj, name, args, context=None):
        orders = [order.strip() for order in args[0][2].split(',')]
        where = [('sale_id.name', 'in', orders)]
        return where

    _columns = {
        'attached_truck_driver_signature': fields.boolean('Attached Truck Driver Signature?',
                                                          help='Follow scan and attach procedure.'),
        'all_product_received':fields.boolean('All Received Products checked?',
                                              help='Warehouseman certifies the products received are counted and quality checked.'),
        'invoice_id' : fields.many2one('account.invoice', 'Invoice'),
        'date_receipt': fields.datetime('Receipt Date'),
        'attached_report_id': fields.many2one('ir.attachment', 'Automatic BOL report'),
        'handling_unit' : fields.char('Handling Units', size=64),
        'hu_type': fields.char('HU Type', size=64),
        'nmfc': fields.char('NMFC#', size=64),
        'p_class': fields.char('Class', size=64),
        'attached_mbol_report_id': fields.many2one('ir.attachment', 'Automatic Master BOL report'),
        'full_name': fields.function(_get_full_name, type='char', string='Sale Order', fnct_search=_search_orders),
        'picking_no': fields.integer('Picking NO.', invisible=True),
        'active': fields.boolean('Active'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('auto', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('historical','Historical'),
            ], 'State', readonly=True, select=True,
            help="* Draft: not confirmed yet and will not be scheduled until confirmed\n"\
                 "* Confirmed: still waiting for the availability of products\n"\
                 "* Available: products reserved, simply waiting for confirmation.\n"\
                 "* Waiting: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"\
                 "* Done: has been processed, can't be modified or cancelled anymore\n"\
                 "* Cancelled: has been cancelled, can't be confirmed anymore"),
    }

    _defaults ={
        'active':True
        }

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        sale_obj = self.pool.get('sale.order')
        if vals.get('sale_id', False):
            sale_rec = sale_obj.browse(cr, uid, vals['sale_id'], context=context)
            vals.update({'picking_no': (len(sale_rec.picking_ids))})
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(stock_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if not context.get('display_bol',False):
            if res.get('toolbar'):
                res.get('toolbar').update({'relate' : []})
        return res


#     def copy(self, cr, uid, id, default=None, context=None):
#         if default is None:
#             default = {}
#         #default.update({
#             #    'attached_truck_driver_signature': False,
#             #    'all_product_received': False,
#             #})
#         res_id = super(stock_picking, self).copy(cr, uid, id, default, context=context)
#         return res_id

    def action_process(self, cr, uid, ids, context=None):
        #import pdb; pdb.set_trace()  # XXX BREAKPOINT
        for pick in self.browse(cr, uid, ids):
            if pick.type =='in' and not pick.pod_scan_num:
                raise osv.except_osv(_('Warning !'), _('Please specify POD # before processing the shipment !'))
        ret = super(stock_picking, self).action_process(cr, uid, ids, context=context)
        return ret

    def _invoice_hook(self, cursor, user, picking, invoice_id):
        if invoice_id:
            self.write(cursor, user, [picking.id], {'invoice_id': invoice_id})
        return super(stock_picking, self)._invoice_hook(cursor, user, picking, invoice_id)
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id],
                               {'name': sequence_obj.get(cr, uid,
                                'stock.picking.%s'%(pick.type)),
                               })
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            'prodlot_id': False,
                            'tracking_id': False,
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                delivered_pack_id = new_picking
                back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                self.message_post(cr, uid, ids, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
                # Then we finish the good picking for incoming shipment
                if pick.type == 'in':
                    self.action_move(cr, uid, [new_picking], context=context)
                    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                    wf_service.trg_write(uid, 'stock.picking', pick.id, cr)

            else:
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

    '''def do_partial(self, cr, uid, ids, partial_datas, context=None):
        res = super(stock_picking, self).do_partial(cr, uid, ids, partial_datas, context=context)
        pool_attachs = self.pool.get('ir.attachment')
        for rec in res.keys():
            if int(rec) != int(res[int(rec)]['delivered_picking']):
                att_ids = pool_attachs.search(cr, uid, [('res_id','=',int(rec)),('res_model','=','stock.picking')])
                if att_ids:
                    pool_attachs.write(cr, uid, att_ids, {'res_id':int(res[int(rec)]['delivered_picking'])})
                self.write(cr, uid, [int(rec)], {'pod_scan_num':False,'attached_truck_driver_signature': False,'all_product_received': False})
        return res'''

        # FIXME: needs refactoring, this code is partially duplicated in stock_move.do_partial()!
#     def do_partial(self, cr, uid, ids, partial_datas, context=None):
#         """ Makes partial picking and moves done.
#         @param partial_datas : Dictionary containing details of partial picking
#                           like partner_id, address_id, delivery_date,
#                           delivery moves with product_id, product_qty, uom
#         @return: Dictionary of values
#         """
#         if context is None:
#             context = {}
#         else:
#             context = dict(context)
#         res = {}
#         move_obj = self.pool.get('stock.move')
#         product_obj = self.pool.get('product.product')
#         currency_obj = self.pool.get('res.currency')
#         uom_obj = self.pool.get('product.uom')
#         sequence_obj = self.pool.get('ir.sequence')
#         pool_attachs = self.pool.get('ir.attachment')
#         wf_service = netsvc.LocalService("workflow")
#         for pick in self.browse(cr, uid, ids, context=context):
#             new_picking = None
#             complete, too_many, too_few = [], [], []
#             move_product_qty = {}
#             prodlot_ids = {}
#             product_avail = {}
#             for move in pick.move_lines:
#                 if move.state in ('done', 'cancel'):
#                     continue
#                 partial_data = partial_datas.get('move%s'%(move.id), {})
#                 #Commented in order to process the less number of stock moves from partial picking wizard
#                 #assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
#                 product_qty = partial_data.get('product_qty') or 0.0
#                 move_product_qty[move.id] = product_qty
#                 product_uom = partial_data.get('product_uom') or False
#                 product_price = partial_data.get('product_price') or 0.0
#                 product_currency = partial_data.get('product_currency') or False
#                 prodlot_id = partial_data.get('prodlot_id') or False
#                 prodlot_ids[move.id] = prodlot_id
#                 if move.product_qty == product_qty:
#                     complete.append(move)
#                 elif move.product_qty > product_qty:
#                     too_few.append(move)
#                 else:
#                     too_many.append(move)
#
#                 # Average price computation
#                 if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
#                     product = product_obj.browse(cr, uid, move.product_id.id)
#                     move_currency_id = move.company_id.currency_id.id
#                     context['currency_id'] = move_currency_id
#                     qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
#
#                     if product.id in product_avail:
#                         product_avail[product.id] += qty
#                     else:
#                         product_avail[product.id] = product.qty_available
#
#                     if qty > 0:
#                         new_price = currency_obj.compute(cr, uid, product_currency,
#                                 move_currency_id, product_price)
#                         new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
#                                 product.uom_id.id)
#                         if product.qty_available <= 0:
#                             new_std_price = new_price
#                         else:
#                             # Get the standard price
#                             amount_unit = product.price_get('standard_price', context)[product.id]
#                             new_std_price = ((amount_unit * product_avail[product.id])\
#                                 + (new_price * qty))/(product_avail[product.id] + qty)
#                         # Write the field according to price type field
#                         product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
#
#                         # Record the values that were chosen in the wizard, so they can be
#                         # used for inventory valuation if real-time valuation is enabled.
#                         move_obj.write(cr, uid, [move.id],
#                                 {'price_unit': product_price,
#                                  'price_currency_id': product_currency})
#
#
#             for move in too_few:
#                 product_qty = move_product_qty[move.id]
#
#                 if not new_picking:
#                     new_picking = self.copy(cr, uid, pick.id,
#                             {
#                                 'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
#                                 'move_lines' : [],
#                                 'state':'draft',
#                             })
#                 if product_qty != 0:
#                     defaults = {
#                             'product_qty' : product_qty,
#                             'product_uos_qty': product_qty, #TODO: put correct uos_qty
#                             'picking_id' : new_picking,
#                             'state': 'assigned',
#                             'move_dest_id': False,
#                     }
#                     prodlot_id = prodlot_ids[move.id]
#                     if prodlot_id:
#                         defaults.update(prodlot_id=prodlot_id)
#                     move_obj.copy(cr, uid, move.id, defaults)
#
#                 move_obj.write(cr, uid, [move.id],
#                         {
#                             'product_qty' : move.product_qty - product_qty,
#                             'product_uos_qty':move.product_qty - product_qty, #TODO: put correct uos_qty
#                         })
#
#             if new_picking:
#                 move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
#             for move in complete:
#                 if prodlot_ids.get(move.id):
#                     move_obj.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids[move.id]})
#             for move in too_many:
#                 product_qty = move_product_qty[move.id]
#                 defaults = {
#                     'product_qty' : product_qty,
#                     'product_uos_qty': product_qty, #TODO: put correct uos_qty
#                 }
#                 prodlot_id = prodlot_ids.get(move.id)
#                 if prodlot_ids.get(move.id):
#                     defaults.update(prodlot_id=prodlot_id)
#                 if new_picking:
#                     defaults.update(picking_id=new_picking)
#                 move_obj.write(cr, uid, [move.id], defaults)
#
#
#             # At first we confirm the new picking (if necessary)
#             if new_picking and pick.type == 'out':
#                 wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
#                 # Then we finish the good picking
#                 self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
# #                self.action_move(cr, uid, [new_picking])
#                 #wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
#                 wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
#                 delivered_pack_id = new_picking
#             else:
#                 self.action_move(cr, uid, [pick.id])
#                 wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
#                 delivered_pack_id = pick.id
# #            att_ids = pool_attachs.search(cr, uid, [('res_id','=',delivered_pack_id),('res_model','=','stock.picking')])
# #            if att_ids:
# #                pool_attachs.write(cr, uid, att_ids, {'res_id':delivered_pack_id})
# #                self.write(cr, uid, [delivered_pack_id], {'pod_scan_num':False,'attached_truck_driver_signature': False,'all_product_received': False})
#
#             delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
#             res[pick.id] = {'delivered_picking': delivered_pack.id or False}
#
#         return res

    def action_done(self, cr, uid, ids, context=None):
        """ Changes picking state to done.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')})
#         self.log_picking(cr, uid, ids, context=context)
        return True

class stock_picking_in(osv.Model):

    _inherit = 'stock.picking.in'

    _columns = {
        'attached_truck_driver_signature': fields.boolean('Attached Truck Driver Signature?',
                                                          help='Follow scan and attach procedure.'),
        'all_product_received':fields.boolean('All Received Products checked?',
                                              help='Warehouseman certifies the products received are counted and quality checked.'),
        'invoice_id' : fields.many2one('account.invoice', 'Invoice'),
        'date_receipt': fields.datetime('Receipt Date'),
        }

class stock_picking_out(osv.Model):

    _inherit = 'stock.picking.out'

    _columns = {
        'handling_unit' : fields.char('Handling Units', size=64),
        'hu_type': fields.char('HU Type', size=64),
        'nmfc': fields.char('NMFC#', size=64),
        'p_class': fields.char('Class', size=64),
        'invoice_id' : fields.many2one('account.invoice', 'Invoice'),
        'active': fields.boolean('Active'),
        'picking_no': fields.integer('Picking NO.', invisible=True),
        'attached_mbol_report_id': fields.many2one('ir.attachment', 'Automatic Master BOL report'),
        'attached_report_id': fields.many2one('ir.attachment', 'Automatic BOL report'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('auto', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('historical','Historical'),
            ], 'State', readonly=True, select=True,
            help="* Draft: not confirmed yet and will not be scheduled until confirmed\n"\
                 "* Confirmed: still waiting for the availability of products\n"\
                 "* Available: products reserved, simply waiting for confirmation.\n"\
                 "* Waiting: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"\
                 "* Done: has been processed, can't be modified or cancelled anymore\n"\
                 "* Cancelled: has been cancelled, can't be confirmed anymore"),
        }
    _defaults ={
        'active':True
        }

class stock_move(osv.Model):
    _inherit = "stock.move"
    _columns = {
        'active': fields.boolean('Active'),
        'state': fields.selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Not Available'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled'),('historical','Historical')], 'State', readonly=True, select=True,
              help='When the stock move is created it is in the \'Draft\' state.\n After that, it is set to \'Not Available\' state if the scheduler did not find the products.\n When products are reserved it is set to \'Available\'.\n When the picking is done the state is \'Done\'.\
              \nThe state is \'Waiting\' if the move is waiting for another one.'),
    }

    _defaults ={
        'active':True
    }

class product_product(osv.Model):

    _inherit = 'product.product'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'default_code':''})
        return super(product_product,self).copy(cr, uid, id, default=default, context=context)

    def _check_unique_product_code(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            rec_ids = self.search(cr, uid, [('default_code','!=',False),('default_code','=',rec.default_code),('id','!=',rec.id)], context=context)
            if rec_ids:
                return False
        return True

    _constraints = [
        (_check_unique_product_code, _('The code(Reference) must be unique per product!'), ['default_code']),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: