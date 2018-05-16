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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class mrp_repair(osv.Model):
    _inherit = 'mrp.repair'
    _columns = {
              'technician_id':fields.many2one('res.users', 'Technician'),
              'courier_type' : fields.selection([('ups', 'UPS'), ('fedex', 'FEDEX'), ('usps', 'USPS'), ('dhl', 'DHL'), ('drop', 'Drop-off'), ('other', 'Other')], 'Courier Type'),
              'box' : fields.selection([('yes', 'Yes'), ('no', 'No')], 'Original Box'),
              'condition' : fields.selection([('yes', 'Yes'), ('no', 'No')], 'New condition'),
              'accessory' : fields.text('Accessories', size=1024),
              'damaged_area' : fields.text('Visible Damage', size=1024),
              'component' : fields.text('Component Serials', size=1024),
              'guarantee_limit': fields.date('Guarantee limit', readonly=True, help="The guarantee limit is computed as: last move date + warranty stamped on the last move. If the current date is below the guarantee limit, each operation and fee you will add will be set as 'not to invoiced' by default. Note that you can change manually afterwards."),
              'tracking_no': fields.char('Tracking No', size=64)
              }
    
    def create(self, cr, uid, vals, context=None):
        if vals.has_key('move_id') and vals['move_id'] and vals.has_key('product_id') and vals['product_id']:
            move =  self.pool.get('stock.move').browse(cr, uid,vals['move_id'])
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            limit = datetime.strptime(move.date_expected, '%Y-%m-%d %H:%M:%S') + relativedelta(months=int(product.warranty))
            vals['guarantee_limit'] = limit.strftime('%Y-%m-%d')
        return super(mrp_repair, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid,ids, vals, context=None):
        for repair in self.browse(cr,uid,ids):
            prod_id=repair.product_id.id
            move_id=repair.move_id.id
        if vals.has_key('move_id') and vals['move_id']:
            move_id=vals['move_id']
        if vals.has_key('product_id') and vals['product_id']:
            prod_id=vals['product_id']
        move =  self.pool.get('stock.move').browse(cr, uid,move_id)
        product = self.pool.get('product.product').browse(cr, uid, prod_id)
        limit = datetime.strptime(move.date_expected, '%Y-%m-%d %H:%M:%S') + relativedelta(months=int(product.warranty))
        vals['guarantee_limit'] = limit.strftime('%Y-%m-%d')   
        return super(mrp_repair, self).write(cr, uid,ids, vals, context=context)

    def action_repair_done(self, cr, uid, ids, context=None):
        res = super(mrp_repair, self).action_repair_done(cr, uid, ids, context)
        repair_id = self.pool.get('crm.rma.line').search(cr, uid, [('repair_id', 'in', ids)])
        if repair_id:
            rma_id = self.pool.get('crm.rma.line').browse(cr, uid, repair_id[0]).rma_id.id
            rma_obj = self.pool.get('crm.rma').browse(cr, uid, rma_id)
            for line in rma_obj.rma_lines:
                repaired = line.repair_id.repaired
                if not repaired :
                    break
            if repaired:
                self.pool.get('crm.rma').write(cr, uid, [rma_id], {'state':'repaired'})
        return res

class mrp_repair_category(osv.Model):
        _name = 'mrp.repair.category'
        _columns = {
              'name':fields.char('Name', size=64, required=True),
              }

class mrp_repair_component(osv.Model):
        _name = 'mrp.repair.component'
        _columns = {
              'name':fields.char('Name', size=64, required=True),
              'category_id':fields.many2one('mrp.repair.category', 'Category'),
              }

class mrp_repair_symptom(osv.Model):
        _name = 'mrp.repair.symptom'
        _columns = {
              'name':fields.char('Name', size=64, required=True),
              'compo_id':fields.many2one('mrp.repair.component', 'Component'),
              }

class mrp_repair_action(osv.Model):
        _name = 'mrp.repair.action'
        _columns = {
              'name':fields.char('Name', size=64, required=True),
              'sympt_id':fields.many2one('mrp.repair.symptom', 'Symptom'),
              }

class mrp_repair_line(osv.Model):
    _inherit = 'mrp.repair.line'
    _columns = {
              'categ_id':fields.many2one('mrp.repair.category', 'Category'),
              'component_id':fields.many2one('mrp.repair.component', 'Component'),
              'symptom_id':fields.many2one('mrp.repair.symptom', 'Symptom'),
              'action_id':fields.many2one('mrp.repair.action', 'Action Taken'),
              'symptom_note':fields.text('Symptom Notes', size=1024),
              }
    
    def onchange_operation_type(self, cr, uid, ids, type, guarantee_limit, company_id=False, context=None):
        """ On change of operation type it sets source location, destination location
        and to invoice field.
        @param product: Changed operation type.
        @param guarantee_limit: Guarantee limit of current record.
        @return: Dictionary of values.
        """
        res = super(mrp_repair_line, self).onchange_operation_type(cr, uid, ids, type, guarantee_limit, company_id, context)
        warehouse_obj = self.pool.get('stock.warehouse')
        warehouse_ids = warehouse_obj.search(cr, uid, [])
        if warehouse_ids:
            warehouse = warehouse_obj.browse(cr, uid, warehouse_ids[0])
            if type == 'add':
                res['value'].update({'location_dest_id': warehouse.lot_return_id.id})
            elif type == 'remove':
                res['value'].update({'location_id': warehouse.lot_return_id.id})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
