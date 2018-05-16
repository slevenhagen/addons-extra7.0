# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT as DT,
                           DEFAULT_SERVER_DATETIME_FORMAT as DDT)
import time

def date_to_datetime(date):
    return time.strftime(DDT, time.strptime(date, DT))

class open_picking_list(orm.TransientModel):
    _name = 'open.picking.list'
    _description = 'Open Picking list from partner'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'date_from': fields.date('Date from'),
        'date_to': fields.date('Date to'),
        'type': fields.selection([
                                  ('out', 'Sending Goods'),
                                  ('in', 'Getting Goods'),
                                  ('internal', 'Internal')
                                  ], 'Shipping Type', required=True)
    }

    _defaults = {
        'type': 'out',
    }

    def _check_date(self, cr, uid, ids, context=None):
        """
        Check if date to is greater than date from
        """
        if context is None:
            context = {}
        res = True
        for record in self.browse(cr, uid, ids, context=context):
            if record.date_from and record.date_to and \
                record.date_from > record.date_to:
                res = False
        return res

    _constraints = [
        (_check_date,
         'The end date of the period should be greater than the start date',
         ['date_from', 'date_to']),
    ]

    def open_list(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        record = self.browse(cr, uid, ids[0], context=context)
        type = record.type
        partner_id = record.partner_id.id
        if type == 'in':
            result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
        elif type == 'out':
            result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        else:
            result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree6')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        action_context = eval(result['context'])
        action_context.update({'search_default_partner_id': partner_id})
        domain = result['domain'] and eval(result['domain']) or []
        if record.date_from:
            date = date_to_datetime(record.date_from)
            domain += ['|', ('date_done', '>=', date), '&', ('date_done', '=', False), ('min_date', '>=', date)]
        if record.date_to:
            date = date_to_datetime(record.date_to)
            domain += ['|', ('date_done', '<=', date), '&', ('date_done', '=', False), ('min_date', '<=', date)]
        result['domain'] = str(domain)
        result['context'] = str(action_context)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
