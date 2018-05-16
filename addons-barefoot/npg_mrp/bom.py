# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2015 NovaPoint Group INC (<http://www.novapointgroup.com>)
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
from openerp import tools, SUPERUSER_ID
from openerp.tools.translate import _
from openerp.addons.product import _common
from openerp import netsvc
import time
from operator import itemgetter
import pytz
from datetime import datetime, timedelta
from dateutil import rrule
import math
# from faces import *
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _
from itertools import groupby


class mrp_bom(osv.Model):
    _inherit = "mrp.bom"
    
    def _check_product(self, cr, uid, ids, context=None):
        return True
        #=======================================================================
        # all_prod = []
        # boms = self.browse(cr, uid, ids, context=context)
        # def check_bom(boms):
        #     res = True
        #     for bom in boms:
        #         if bom.product_id.id in all_prod:
        #             res = res and False
        #         all_prod.append(bom.product_id.id)
        #         lines = bom.bom_lines
        #         if lines:
        #             res = res and check_bom([bom_id for bom_id in lines if bom_id not in boms])
        #     return res
        # return check_bom(boms)
        #=======================================================================
    
    
    
    def _has_bom(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        
        boms = self.browse(cr,uid,ids,context=context)
        
        bom_obj = self.pool.get('mrp.bom')
        
        for bom in boms:
            ids = bom_obj.search(cr,uid,[('product_id','=',bom.product_id.id),('bom_id','=', None )])
            if ids:
                res[bom.id] = True
            else:
                res[bom.id] = False
        
        return res
    
    _columns = {
            'name': fields.char('BOM Name', size=64),
#             'workcenter_id': fields.many2one('mrp.workcenter', 'Work Center', required=False, help="Work center in parent BOM Routing where product to be consumed"),
            'routing_job_id': fields.many2one('mrp.routing.workcenter', 'Operation', required=False, help="Work center in parent BOM Routing where product to be consumed"),
            'has_bom': fields.function(_has_bom, type='boolean', string='Has BOM', help='If field True if Product has Bill of Material'),
            'source_location_id': fields.many2one('stock.location', 'Source Location', required=False,),
        }
#    _order ='sequence'
    
    def onchange_routing(self, cr, uid, ids, routing_id, context={}):
        return True
    
    def open_component_bom(self,cr,uid, ids, context=None):
        
        bom_obj = self.browse(cr,uid,ids,context=context)
        product_id = False
        for bom in bom_obj:
            
            product_id = bom.product_id.id
            
#        print " BOM:%s Product: %s"%(ids, product_id)  
            
#        context['default_product_id'] = product_id

        
        context['search_default_product_id'] = product_id
        if context.get('view_mode') == 'form':
            view_mode = 'form,tree'
        else:
            view_mode = 'tree,form'
                
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr,uid,'mrp','mrp_bom_tree_view')
        view_id = view_ref and view_ref[1] or False
        vals = {
                'name': _('Bill of Materials'),
                 'view_type': 'form',
                 'view_mode': view_mode,
 #                'view_id': view_id,
                 'res_model': 'mrp.bom',
                 'context': context,
                 'domain': [('bom_id','=',False)],
                 'target': 'current',
                 'nodestroy': True,
                 'res_id':  ids[0],
                 'type': 'ir.actions.act_window',}
#        print vals
        return vals
    
    def open_product(self,cr,uid, ids, context=None):
        
        bom_obj = self.browse(cr,uid,ids,context=context)
        product_id = False
        for bom in bom_obj:
            
            product_id = bom.product_id.id
            
                
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr,uid,'product','product_normal_form_view')
        view_id = view_ref and view_ref[1] or False
        vals = {
                'name': _('Product'),
                 'view_type': 'form',
                 'view_mode': 'form',
                 'view_id': view_id,
                 'res_model': 'product.product',
                 'context': context,
                 'target': 'current',
                 'nodestroy': True,
                 'res_id':  product_id,
                 'type': 'ir.actions.act_window',}
#        print vals
        return vals

    #===========================================================================
    # def _bom_explode(self, cr, uid, bom, factor, properties=None, addthis=False, level=0, routing_id=False):
    #     result, result2 = super(mrp_bom, self)._bom_explode(cr, uid, bom, factor, properties, addthis, level, routing_id)
    #     result.update({'workcenter_id' : bom.workcenter_id and bom.workcenter_id.id or False})
    #     return result, result2
    #===========================================================================
    
    def _bom_explode(self, cr, uid, bom, factor, properties=None, addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = _common.ceiling(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)

            if newbom and newbom != bom.id:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                    'workcenter_id' : bom.routing_job_id and bom.routing_job_id.workcenter_id.id or False,
                    'source_location_id' : bom.source_location_id and bom.source_location_id.id or False,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level+(wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                        'check_prior' : wc_use.check_prior,
                        'production_location_id' : wc_use.production_location_id and wc_use.production_location_id.id or False,
                        'wo_attatch' : wc_use.wo_attatch,
                        'datas_fname':wc_use.datas_fname,
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2

class StockMove(osv.osv):
    _inherit = 'stock.move'
    
    _columns = {
        'work_order_id': fields.many2one('mrp.production.workcenter.line', 'Work Order', select=True, readonly=True),
    }
StockMove()  
class production_order(osv.osv):
    _inherit = 'mrp.production'
    
    def _make_production_internal_shipment_line(self, cr, uid, production_line, shipment_id, parent_move_id, destination_location_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        wc_obj = self.pool.get('mrp.production.workcenter.line')
        production = production_line.production_id
        date_planned = production.date_planned
        # Internal shipment is created for Stockable and Consumer Products
        if production_line.product_id.type not in ('product', 'consu'):
            return False
        source_location_id = production.location_src_id.id
        if production_line.source_location_id:
            source_location_id = production_line.source_location_id.id
            
        if not destination_location_id:
            destination_location_id = production.location_src_id.id
        
        bom_wc = production_line.workcenter_id and production_line.workcenter_id.id or False
        wc_ids = []
        if bom_wc:
            wc_ids = wc_obj.search(cr,uid,[('production_id','=',production_line.production_id.id),('workcenter_id','=',bom_wc)])
        wcid = wc_ids and wc_ids[0] or False
        if wcid:
            prod = wc_obj.browse(cr,uid,wcid,context).production_location_id
            destination_location_id = prod and prod.id or destination_location_id
            
        return stock_move.create(cr, uid, {
                        'name': production.name,
                        'picking_id': shipment_id,
                        'product_id': production_line.product_id.id,
                        'product_qty': production_line.product_qty,
                        'product_uom': production_line.product_uom.id,
                        'product_uos_qty': production_line.product_uos and production_line.product_uos_qty or False,
                        'product_uos': production_line.product_uos and production_line.product_uos.id or False,
                        'date': date_planned,
                        'move_dest_id': parent_move_id,
                        'location_id': source_location_id,
                        'location_dest_id': destination_location_id,
                        'state': 'waiting',
                        'company_id': production.company_id.id,
                })
    
    def _make_production_consume_line(self, cr, uid, production_line, parent_move_id, source_location_id=False, context=None):
        stock_move = self.pool.get('stock.move')
        wc_obj = self.pool.get('mrp.production.workcenter.line')
        production = production_line.production_id
        # Internal shipment is created for Stockable and Consumer Products
        if production_line.product_id.type not in ('product', 'consu'):
            return False
        destination_location_id = production.product_id.property_stock_production.id
        if not source_location_id:
            source_location_id = production.location_src_id.id
#         if production_line.source_location_id:
#             source_location_id = production_line.source_location_id.id
            
        bom_wc = production_line.workcenter_id and production_line.workcenter_id.id or False
        wc_ids = []
        if bom_wc:
            wc_ids = wc_obj.search(cr,uid,[('production_id','=',production_line.production_id.id),('workcenter_id','=',bom_wc)])
        wcid = wc_ids and wc_ids[0] or False
        if wcid:
            prod = wc_obj.browse(cr,uid,wcid,context).production_location_id
            source_location_id = prod and prod.id or source_location_id
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'product_id': production_line.product_id.id,
            'product_qty': production_line.product_qty,
            'product_uom': production_line.product_uom.id,
            'product_uos_qty': production_line.product_uos and production_line.product_uos_qty or False,
            'product_uos': production_line.product_uos and production_line.product_uos.id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'move_dest_id': parent_move_id,
            'state': 'waiting',
            'company_id': production.company_id.id,
            'work_order_id':wcid,
        })
        production.write({'move_lines': [(4, move_id)]}, context=context)
        return move_id
    
    def action_confirm(self, cr, uid, ids, context=None):
        shipment_id = super(production_order, self).action_confirm(cr, uid, ids, context)
        wf_service = netsvc.LocalService("workflow")
        for production in self.browse(cr, uid, ids, context=context):
            for wc_id in production.workcenter_lines:
                wf_service.trg_validate(uid, 'mrp.production.workcenter.line', wc_id.id, 'button_check', cr)
                wf_service.trg_write(uid, 'mrp.production.workcenter.line', wc_id.id, cr)
                wf_service.trg_trigger(uid, 'mrp.production.workcenter.line', wc_id.id, cr)
        return shipment_id
    
    
    def _compute_planned_workcenter(self, cr, uid, ids, context=None, mini=False):
        """ Computes planned and finished dates for work order.
        @return: Calculated date
        """
        dt_end = datetime.now()
        if context is None:
            context = {}
        for po in self.browse(cr, uid, ids, context=context):
            dt_end = datetime.strptime(po.date_planned, '%Y-%m-%d %H:%M:%S')
            if not po.date_start:
                self.write(cr, uid, [po.id], {
                    'date_start': po.date_planned
                }, context=context, update=False)
            old = None
            for wci in range(len(po.workcenter_lines)):
                wc  = po.workcenter_lines[wci]
                if (old is None) or (wc.sequence>old):
                    dt = dt_end
                    
                #===============================================================
                # Condition added for check prior
                #===============================================================
                if not wc.check_prior:
                    dt = datetime.strptime(po.date_planned, '%Y-%m-%d %H:%M:%S')
                    
                    
                if context.get('__last_update'):
                    del context['__last_update']
                if (wc.date_planned < dt.strftime('%Y-%m-%d %H:%M:%S')) or mini:
                    self.pool.get('mrp.production.workcenter.line').write(cr, uid, [wc.id],  {
                        'date_planned': dt.strftime('%Y-%m-%d %H:%M:%S')
                    }, context=context, update=False)
                    i = self.pool.get('resource.calendar').interval_get(
                        cr,
                        uid,
                        wc.workcenter_id.calendar_id and wc.workcenter_id.calendar_id.id or False,
                        dt,
                        wc.hour or 0.0
                    )
                    if i:
                        dt_end = max(dt_end, i[-1][1])
                else:
                    dt_end = datetime.strptime(wc.date_planned_end, '%Y-%m-%d %H:%M:%S')

                old = wc.sequence or 0
            super(production_order, self).write(cr, uid, [po.id], {
                'date_finished': dt_end
            })
        return dt_end
    
production_order()
class mrp_production_product_line(osv.osv):
    _inherit = 'mrp.production.product.line'
    _columns = {
        'workcenter_id': fields.many2one('mrp.workcenter', 'Work Center', select=True, readonly=True),
        'source_location_id': fields.many2one('stock.location', 'Source Location', required=False,),
    }
mrp_production_product_line()
class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    _columns = {
                 'state': fields.selection([('new','New'),('wait_work','Waiting Work'),('wait_product','Waiting Product'),('draft','Ready'),('cancel','Cancelled'),('pause','Pending'),('startworking', 'In Progress'),('done','Finished')],'Status', readonly=True, copy=False,
                                 help="* When a work order is created it is set in 'Draft' status.\n" \
                                       "* When user sets work order in start mode that time it will be set in 'In Progress' status.\n" \
                                       "* When work order is in running mode, during that time if user wants to stop or to make changes in order then can set in 'Pending' status.\n" \
                                       "* When the user cancels the work order it will be set in 'Canceled' status.\n" \
                                       "* When order is completely processed that time it is set in 'Finished' status."),
                'move_ids' : fields.one2many('stock.move','work_order_id', string="Raw Materials"),
                'check_prior':fields.boolean("Complete Prior Work"),
                'production_location_id': fields.many2one('stock.location', 'Production Location', required=False,
                                                           readonly=True, states={'draft':[('readonly',False)]},
                                                         help="Location where the Raw materials will be consumed for the Job."),
                
                'wo_attatch':fields.binary('WorkOrder Attachment'),
                'datas_fname':fields.char('File Name',size=256),
    }
    
    _defaults = {
        'state': 'new',
        }
    
    def wo_get(self, cr, uid, ids, context=None):
        if not ids: return []
        for wo in self.browse(cr,uid,ids,context):
            if wo.check_prior:
                wos = self.search(cr,uid,[('production_id','=',wo.production_id.id)])
                all_seq = [w.sequence for w in self.browse(cr,uid,wos,context)]
                all_seq.sort()
                seq = wo.sequence
                ind = seq in all_seq and all_seq.index(seq) or False
                if not ind:
                    continue
                prev_seq = all_seq[ind-1]
                prev_wo = self.search(cr,uid,[('production_id','=',wo.production_id.id),('sequence','=',prev_seq)])
                return prev_wo
        return []
    
    def move_get(self, cr, uid, ids, context=None):
        if not ids: return []
        mvs = []
        for wo in self.browse(cr,uid,ids,context):
            mvs.extend([mv.id for mv in wo.move_ids])
        return mvs
    
    def action_new(self, cr, uid, ids, context=None):
        """ Sets state to new.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'new'}, context=context)
    
    def action_waiting_work(self, cr, uid, ids, context=None):
        """ Sets state to wait_work.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'wait_work'}, context=context)
    
    def action_wait_product(self, cr, uid, ids, context=None):
        """ Sets state to wait products.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'wait_product'}, context=context)
    
    def test_wait_work(self, cr, uid, ids, context=None):
        res = True
        for wo in self.browse(cr,uid,ids,context):
            if wo.check_prior:
                wos = self.search(cr,uid,[('production_id','=',wo.production_id.id)])
                all_seq = [w.sequence for w in self.browse(cr,uid,wos,context)]
                all_seq.sort()
                seq = wo.sequence
                ind = seq in all_seq and all_seq.index(seq) or False
                if not ind:
                    continue
                prev_seq = all_seq[ind-1]
                prev_wo = self.search(cr,uid,[('production_id','=',wo.production_id.id),('sequence','=',prev_seq)])
                pwo = self.browse(cr,uid,prev_wo[0])
                if prev_wo and pwo.state!='done':
                    res = False
#                     raise osv.except_osv(_('Warning!'), _('Previous work order %s should be finished first!')%(pwo.name))
        return res
    
    def test_rawmaterial(self, cr, uid, ids, context=None):
        """ Check Raw materials availability.
        @return: True
        """
        for wo in self.browse(cr,uid,ids,context):
            for move in wo.move_ids:
                if move.state in ['assigned','done']:
                    continue
                else:
                    return False
#                     raise osv.except_osv(_('Warning!'), _('All raw materials should be available to start work on this work order'))
        return True
        
    
    def check_prior(self, cr, uid, ids, context=None):
        """ Sets Checks the previous work order is completed or not.
        @return: True
        """
        for wo in self.browse(cr,uid,ids,context):
            if wo.check_prior:
                wos = self.search(cr,uid,[('production_id','=',wo.production_id.id)])
                all_seq = [w.sequence for w in self.browse(cr,uid,wos,context)]
                all_seq.sort()
                seq = wo.sequence
                ind = seq in all_seq and all_seq.index(seq) or False
                if not ind:
                    continue
                prev_seq = all_seq[ind-1]
                prev_wo = self.search(cr,uid,[('production_id','=',wo.production_id.id),('sequence','=',prev_seq)])
                pwo = self.browse(cr,uid,prev_wo[0])
                if prev_wo and pwo.state!='done':
                    raise osv.except_osv(_('Warning!'), _('Previous work order %s should be finished first!')%(pwo.name))
        return True
    
    def check_rawmaterial(self, cr, uid, ids, context=None):
        """ Check Raw materials availability.
        @return: True
        """
        for wo in self.browse(cr,uid,ids,context):
            for move in wo.move_ids:
                if move.state in ['assigned','done']:
                    continue
                else:
                    raise osv.except_osv(_('Warning!'), _('All raw materials should be available to start work on this work order'))
        return True
    
    def action_start_working(self, cr, uid, ids, context=None):
        """ Sets state to start working and writes starting date.
        @return: True
        """
        self.check_rawmaterial(cr,uid,ids,context)
        self.check_prior(cr,uid,ids,context)
        self.modify_production_order_state(cr, uid, ids, 'start')
        self.write(cr, uid, ids, {'state':'startworking', 'date_start': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
    
mrp_production_workcenter_line()

class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'
    _columns = {
                'name': fields.char('Operation', size=64, required=True),
                'check_prior':fields.boolean("Complete Prior Work"),
                'production_location_id': fields.many2one('stock.location', 'Production Location', required=False,
                                                         help="Location where the Raw materials will be consumed for the Job."),
                'wo_attatch':fields.binary('WorkOrder Attachment'),
                'datas_fname':fields.char('File Name',size=256),
    }
  
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','workcenter_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['workcenter_id']:
                name = name + '--'+ record['workcenter_id'][1]
            res.append((record['id'], name))
        return res
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        from_bom = context.get('from_bom', False)
        routing_id = context.get('routing_id', False)
        if from_bom and routing_id:
            args += [('routing_id', '=', routing_id)]
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            ids = []
            if operator in positive_operators:
                ids = self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
                if not ids:
                    ids = self.search(cr, user, [('workcenter_id',operator,name)]+ args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    def open_routing_operation(self,cr,uid, ids, context=None):
        
        line_obj = self.browse(cr,uid,ids,context=context)
        line_id = False
        for line in line_obj:
            
            line_id = line.id
            

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr,uid,'mrp','mrp_routing_workcenter_form_view')
        view_id = view_ref and view_ref[1] or False
        vals = {
                'name': _('Routing Operation'),
                 'view_type': 'form',
                 'view_mode': 'form',
                 'view_id': view_id,
                 'res_model': 'mrp.routing.workcenter',
                 'context': context,
                 'target': 'new',
                 'res_id':  ids[0],
                 
                 'type': 'ir.actions.act_window',}
        
        return vals
    
mrp_routing_workcenter()

# class resource_calendar(osv.osv):
#     _inherit = 'resource.calendar'
# 
#     # def interval_get(self, cr, uid, id, dt_from, hours, resource=False, byday=True):
#     def interval_get_multi(self, cr, uid, date_and_hours_by_cal, resource=False, byday=True):
#         def group(lst, key):
#             lst.sort(key=itemgetter(key))
#             grouped = groupby(lst, itemgetter(key))
#             return dict([(k, [v for v in itr]) for k, itr in grouped])
#         # END group
# 
#         cr.execute("select calendar_id, dayofweek, hour_from, hour_to from resource_calendar_attendance order by hour_from")
#         hour_res = cr.dictfetchall()
#         hours_by_cal = group(hour_res, 'calendar_id')
# 
#         results = {}
#         
# 
#         for d, hours, id in date_and_hours_by_cal:
#             dt_from = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
#             if not id:
#                 td = int(hours)*3
#                 results[(d, hours, id)] = [(dt_from, dt_from + timedelta(hours=td))]
#                 continue
# 
#             dt_leave = self._get_leaves(cr, uid, id, resource)
#             todo = hours
#             result = []
#             maxrecur = 100
#             current_hour = dt_from.hour
#             while float_compare(todo, 0, 4) and maxrecur:
#                 for (hour_from,hour_to) in [(item['hour_from'], item['hour_to']) for item in hours_by_cal[id] if item['dayofweek'] == str(dt_from.weekday())]:
#                     leave_flag  = False
#                     if (hour_to>current_hour) and float_compare(todo, 0, 4):
#                         m = max(hour_from, current_hour)
#                         if (hour_to-m)>todo:
#                             hour_to = m+todo
#                         dt_check = dt_from.strftime('%Y-%m-%d')
#                         for leave in dt_leave:
#                             if dt_check == leave:
#                                 dt_check = datetime.strptime(dt_check, '%Y-%m-%d') + timedelta(days=1)
#                                 leave_flag = True
#                         if leave_flag:
#                             break
#                         else:
#                             d1 = datetime(dt_from.year, dt_from.month, dt_from.day) + timedelta(hours=int(math.floor(m)), minutes=int((m%1) * 60))
#                             d2 = datetime(dt_from.year, dt_from.month, dt_from.day) + timedelta(hours=int(math.floor(hour_to)), minutes=int((hour_to%1) * 60))
#                            
#                             #res_obj.date and res_obj.date_deadline are in UTC in database so we use context_timestamp() to transform them in the `tz` timezone
#                             utc=pytz.UTC
#                             d1 = utc.localize(fields.datetime.context_timestamp(cr, uid, d1, context={}))#datetime.strptime(res_obj.date, tools.DEFAULT_SERVER_DATETIME_FORMAT), context={})
#                             d2 = utc.localize(fields.datetime.context_timestamp(cr, uid, d2, context={}))
#                             
#                             result.append((d1, d2))
#                             current_hour = hour_to
#                             todo -= (hour_to - m)
#                 dt_from += timedelta(days=1)
#                 current_hour = 0
#                 maxrecur -= 1
#             results[(d, hours, id)] = result
#         return results
#     
# resource_calendar()
