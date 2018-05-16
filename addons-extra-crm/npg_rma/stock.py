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

class stock_move(osv.Model):
    _inherit = "stock.move"

    def action_done(self, cr, uid, ids, context=None):
        crm_rma_line_obj = self.pool.get('crm.rma.line')
        repair_obj = self.pool.get('mrp.repair')
        rma_id = crm_rma_line_obj.search(cr, uid, [('incoming_move_id', 'in', ids)])
        for line in self.pool.get('crm.rma.line').browse(cr, uid, rma_id, context=context):
            if line.requested_procedure in ['repair', 'refurbish']:
                # Get the last sale move which would be from Stock to Customer and related calculated guarantee limit
                res = line.product_lot_id and crm_rma_line_obj.get_lst_move_and_limit_from_production_lot(cr, uid, line.product_lot_id)
                move = res and res[0]
                limit = res and res[1]
                vals = {
                        'product_id': line.product_id.id,
                        'partner_id' : line.rma_id.partner_id.id,
                        'address_id': line.rma_id.partner_shipping_id.id,
                        'prodlot_id': line.product_lot_id and line.product_lot_id.id,
                        'location_id': move and move.location_id and move.location_id.id or
                                        line.incoming_move_id.location_dest_id and line.incoming_move_id.location_dest_id.id,
                        'location_dest_id': move and move.location_dest_id and move.location_dest_id.id or
                                        line.rma_id.partner_id.property_stock_customer.id,
                        'move_id': move and move.id or line.incoming_move_id.id,
                        'guarantee_limit': limit and limit.strftime('%Y-%m-%d') or False
                }
                new_vals = repair_obj.onchange_partner_id(cr, uid, [], line.rma_id.partner_id.id, line.rma_id.partner_shipping_id.id)
                vals.update(new_vals['value'])
                repair_id = repair_obj.create(cr, uid, vals, context=context)
                line.write({"repair_id":repair_id})
        return super(stock_move, self).action_done(cr, uid, ids, context)

    _columns = {
        'move_from_sales': fields.boolean('Move from Sales', help="Designates that this move is generated from Sales Order and not from RMA or other process")
    }

class stock_warehouse(osv.Model):
    _inherit = "stock.warehouse"
    _columns = {
        'lot_return_id': fields.many2one('stock.location', 'Location Return', required=True, domain=[('usage', '=', 'internal')]),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
