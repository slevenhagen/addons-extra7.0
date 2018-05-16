
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
from lxml import etree
from openerp.tools.float_utils import float_compare

class stock_partial_picking(osv.Model):
    _inherit = "stock.partial.picking"
    _columns = {
        'attached_truck_driver_signature': fields.boolean('Attached Truck Driver Signature?',
                                                          help='Follow scan and attach procedure.'),
        'all_product_received':fields.boolean('All Received Products checked?',
                                              help='Warehouseman certifies the products received are counted and quality checked.'),
        }

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        pick_obj = self.pool.get('stock.picking')
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        if not picking_ids:
            return res
        result = []
        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            if 'attached_truck_driver_signature' in fields:
                res.update({'attached_truck_driver_signature': pick.attached_truck_driver_signature})
            if 'all_product_received' in fields:
                res.update({'all_product_received': pick.all_product_received})
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        result = super(stock_partial_picking, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        pick_obj = self.pool.get('stock.picking')
        picking_ids = context.get('active_ids', False)

        if not picking_ids:
            # not called through an action (e.g. buildbot), return the default.
            return result

        if view_type != 'form':
            return result

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = context.get('default_type', False)
            if picking_type != pick.type:
                picking_type = pick.type
        _moves_fields = result['fields']
        _moves_arch_lst = """<form string="%s" version="7.0">
                        """ % (_('Process Document'))
        if picking_type == 'in':
            _moves_arch_lst += """<group>
                            <field name="attached_truck_driver_signature" />
                            <field name="all_product_received" />
                            </group>"""
            _moves_fields.update({
                    'attached_truck_driver_signature': {'type':'boolean','string':'Attached Truck Driver Signature?'},
                    'all_product_received':{'type':'boolean','string':'All Received Products checked?'}
                    })
        _moves_arch_lst += """
                        <separator colspan="4" string="%s"/>
                        <field name="%s" colspan="4" nolabel="1" mode="tree" width="550" height="200" ></field>
                        """ % (_('Products'), "move_ids")
        # add field related to picking type only
        if 'move_ids' in _moves_fields.keys():
            _moves_fields['move_ids']['views']['tree']['arch'] = _moves_fields['move_ids']['views']['tree']['arch'].replace('<field name="receive" modifiers="{}"/>',
                                                                         '<field name="receive" string="%s"/>' %(picking_type=='in' and 'Receive' or 'Ship'))
        _moves_arch_lst += """
                <separator string="" colspan="4" />
                <label string="" colspan="2"/>
                <group col="2" colspan="2">
                <button name="do_partial" string="_Validate"
                    colspan="1" type="object" icon="gtk-go-forward" confirm="Quantities Will Be Modified. Click Validate Button Again To Process"/>
            </group>
        </form>"""
        result['arch'] = _moves_arch_lst
        result['fields'] = _moves_fields
        return result

    def do_partial(self, cr, uid, ids, context=None):
        msg_pre = "Incoming shipment '%s' does not have\nthe required Oddello validation.\n"
        msg_post = ""
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        move_receive = 0
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        picking_type = partial.picking_id.type
        if picking_type == 'in':
             if not partial.attached_truck_driver_signature:
                 msg_post += "  * Truck driver signoff\n"
             if not partial.all_product_received:
                 msg_post += "  * Warehouseman signoff\n"
             if msg_post:
                 raise osv.except_osv(_('Warning !'), (msg_pre % (partial.picking_id.name) + msg_post))

             stock_picking.write(cr, uid, [partial.picking_id.id], {'attached_truck_driver_signature':partial.attached_truck_driver_signature,
                                              'all_product_received': partial.all_product_received,
                                              }, context=context)
        for move in partial.move_ids:
             if move.receive:
                move_receive = move_receive + 1
        if move_receive <= 0:
             raise osv.except_osv(_('Warning !'),('Please select atleast one shipment line before proceeding.'))

        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id


            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))
            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:

                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'stock.picking.' + picking_type
                move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                    'product_id': wizard_line.product_id.id,
                                                    'product_qty': wizard_line.quantity,
                                                    'product_uom': wizard_line.product_uom.id,
                                                    'prodlot_id': wizard_line.prodlot_id.id,
                                                    'location_id' : wizard_line.location_id.id,
                                                    'location_dest_id' : wizard_line.location_dest_id.id,
                                                    'picking_id': partial.picking_id.id
                                                    },context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            if wizard_line.receive:
                partial_data['move%s' % (move_id)] = {
                    'product_id': wizard_line.product_id.id,
                    'product_qty': wizard_line.quantity,
                    'product_uom': wizard_line.product_uom.id,
                    'prodlot_id': wizard_line.prodlot_id.id,
                }
                #Should only care about average price when product is received!
                if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                    partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                  product_currency=wizard_line.currency.id)
        stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}

#     def do_partial(self, cr, uid, ids, context=None):
#         result = {}
#         msg_pre = "Incoming shipment '%s' does not have\nthe required Oddello validation.\n"
#         msg_post = ""
#         assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
#         stock_picking = self.pool.get('stock.picking')
#         stock_move = self.pool.get('stock.move')
#         uom_obj = self.pool.get('product.uom')
#         picking_ids = context.get('active_ids', False)
#         partial = self.browse(cr, uid, ids[0], context=context)
#
#         partial_data = {
#             'delivery_date' : partial.date
#         }
#         picking_type = partial.picking_id.type
#         if picking_type == 'in':
#             if not partial.attached_truck_driver_signature:
#                 msg_post += "  * Truck driver signoff\n"
#             if not partial.all_product_received:
#                 msg_post += "  * Warehouseman signoff\n"
#             if msg_post:
#                 raise osv.except_osv(_('Warning !'), (msg_pre % (stock_picking.name) + msg_post))
#
#             stock_picking.write(cr, uid, picking_ids, {'attached_truck_driver_signature':partial.attached_truck_driver_signature,
#                                              'all_product_received': partial.all_product_received,
#                                              }, context=context)
#
#         for wizard_line in partial.move_ids:
#             line_uom = wizard_line.product_uom
#             move_id = wizard_line.move_id.id
#
#             #Quantiny must be Positive
#             if wizard_line.quantity < 0:
#                 raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))
#
#             #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
#             qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)
#
#             if line_uom.factor and line_uom.factor <> 0:
#                 if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
#                     raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
#             if move_id:
#                 #Check rounding Quantity.ex.
#                 #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
#                 #partial delivery: 253g
#                 #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
#                 initial_uom = wizard_line.move_id.product_uom
#                 #Compute the quantity for respective wizard_line in the initial uom
#                 qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
#                 without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
#                 if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
#                     raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
#             else:
#                 seq_obj_name =  'stock.picking.' + picking_type
#                 move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
#                                                     'product_id': wizard_line.product_id.id,
#                                                     'product_qty': wizard_line.quantity,
#                                                     'product_uom': wizard_line.product_uom.id,
#                                                     'prodlot_id': wizard_line.prodlot_id.id,
#                                                     'location_id' : wizard_line.location_id.id,
#                                                     'location_dest_id' : wizard_line.location_dest_id.id,
#                                                     'picking_id': partial.picking_id.id
#                                                     },context=context)
#                 stock_move.action_confirm(cr, uid, [move_id], context)
#             partial_data['move%s' % (move_id)] = {
#                 'product_id': wizard_line.product_id.id,
#                 'product_qty': wizard_line.quantity,
#                 'product_uom': wizard_line.product_uom.id,
#                 'prodlot_id': wizard_line.prodlot_id.id,
#             }
#             if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
#                 partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
#                                                                   product_currency=wizard_line.currency.id)
#         stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
#
#         if stock_picking.state != 'done':
#             show_pick = pick_obj.search(cr, uid, [], limit=1, order='id desc')[0]
#             mod_obj = self.pool.get('ir.model.data')
#             act_obj = self.pool.get('ir.actions.act_window')
#             result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree')
#             id = result and result[1] or False
#             result = act_obj.read(cr, uid, [id], context=context)[0]
#             data = self.read(cr, uid, ids, [])[0]
#             result.update({
#                 'view_mode': 'form',
#                 'view_id': False,
#                 'view_type': 'form',
#                 'res_id': show_pick,
#                 'views': result['views'][1:2]
#             })
#         return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
