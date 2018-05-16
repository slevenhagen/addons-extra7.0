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
import time
from openerp.tools.translate import _

class crm_rma(osv.Model):
    _inherit = 'crm.rma'

    def message_create(self, cr, uid, notes, context=None):
        """ 
         Method to create a message in the history when a user enteres notes in RMA Order.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param notes : Notes added by user.
         @param context : Standard Dictionary
         @return: Identifier of the newly created message.
        """
        if context is None:
            context = {}
        notes = notes or ''
        msg_vals = {
                'name': _("Added Notes on RMA Order: ") + notes,
                'user_id':uid,
            }
        return self.pool.get('crm.rma.message').create(cr, uid, msg_vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """ 
         Over ridden create method to create a message in the history when a user enteres notes in RMA Order.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param vals : Values to create a record
         @param context : Standard Dictionary
         @return: Identifier of the newly created message.
        """
        if context is None:
            context = {}
        if vals.get('note', ''):
            msg_id = self.message_create(cr, uid, vals['note'], context=context)
            msg_ids = vals.get('message_ids', [])
            msg_ids.append(msg_id)
            vals.update({'message_ids': [(6, 0, (msg_ids))]})
        return super(crm_rma, self).create(cr, uid, vals, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'message_ids' : [],
        })
        return super(crm_rma, self).copy(cr, uid, id, default, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        """ 
         Over ridden write method to create a message in the history when a user updates notes in RMA Order.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param ids: List of ids.
         @param vals : Values to update a record
         @param context : Standard Dictionary
         @return: True
        """
        if context is None:
            context = {}
        if 'note' in vals:
            rma = self.browse(cr, uid, ids[0], context=context)
            msg_ids = [msg.id for msg in rma.message_ids]
            msg_ids += vals.get('message_ids', [])
            msg_id = self.message_create(cr, uid, vals['note'], context=context)
            msg_ids.append(msg_id)
            vals.update({'message_ids':[(6, 0, (msg_ids))]})
        return super(crm_rma, self).write(cr, uid, ids, vals, context=context)

class crm_rma_line(osv.Model):
    _inherit = 'crm.rma.line'

    _columns = {
        'product_note': fields.text('Notes', size=256, readonly=False) 
    }
    
    def get_str(self, note, name):
        """ 
         Update the note to differentiate whether it was edited from RMA Order or RMA Line.
         @param self: The object pointer.
         @param note: Note entered by the user
         @return: Updated notes
        """
        note = note or ''
        notes = _("Added Notes on RMA Line: %s : \n" ) % (name) + note
        return notes
    
#    def create(self, cr, uid, vals, context=None):
        """ 
         Over ridden create method to create a message in the history when a user enteres notes in RMA Order Line.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param vals : Values to create a record
         @param context : Standard Dictionary
         @return: Identifier of the newly created message.
        """
        if context is None:
            context = {}
        line_id = super(crm_rma_line, self).create(cr, uid, vals, context=context)
        if vals.get('product_note', ''):
            notes = self.get_str(vals['product_note'], vals['name'])
            self.pool.get('crm.rma.message').historize_message(cr, uid, notes,
                                                               vals.get('rma_id'), context=context)
        return line_id

    
    def write(self, cr, uid, ids, vals, context=None):
        """ 
         Over ridden write method to create a message in the history when a user updates notes in RMA Order Line.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param ids: List of ids.
         @param vals : Values to update a record
         @param context : Standard Dictionary
         @return: True
        """
        if context is None:
            context = {}
        if 'product_note' in vals:
            msg_obj = self.pool.get('crm.rma.message')
            lines = self.browse(cr, uid, ids, context=context)
            for line in lines:
                notes = self.get_str(vals['product_note'], line.name)
                msg_obj.historize_message(cr, uid, notes, line.rma_id.id, context=context)
        return super(crm_rma_line, self).write(cr, uid, ids, vals, context=context)

class crm_rma_message(osv.Model):
    _inherit = 'crm.rma.message'
    
    def historize_message(self, cr, uid, notes, rma_id, context=None):
        """ 
         Method to create a message in the history when a user updates notes in RMA Order Line.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param notes: Notes to be updated in the history.
         @param rma_id : Identifier of the RMA Order
         @param context : Standard Dictionary
         @return: True
        """
        if context is None:
            context = {}        
        rma_obj = self.pool.get('crm.rma')
        rma = rma_obj.browse(cr, uid, rma_id, context=context)
        msg_ids = []
        
        if rma.message_ids:
            msg_ids += [msg.id for msg in rma.message_ids]
        msg_vals = {
                'name': notes,
                'user_id':uid,
            }
        msg_id = self.create(cr, uid, msg_vals, context=context)
        msg_ids.append(msg_id)
        rma_vals = {
            'message_ids' : [(6, 0, (msg_ids))],
        }
        return rma_obj.write(cr, uid, [rma.id], rma_vals, context=context)
    
    def _get_message(self, cr, uid, ids, field_name, arg, context=None):
        """ 
         Function's method to get the message in 128 chars to be displayed in the tree view.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: Current Logged in User's Identifier.
         @param ids: List of ids.
         @param field_name : Functional Field's name.
         @param arg : Other Arguments if any.
         @param context : Standard Dictionary
         @return: 
        """
        msgs = self.browse(cr, uid, ids, context=context)
        res = {}
        for msg in msgs:
            res[msg.id] = msg.name and msg.name[:128] or ''
        return res
    
    _columns = {
        'short_message':fields.function(_get_message, method=True, type='text', string='Message'),
        'date':fields.datetime('Date', help="Timestamp of the comment made by User"),
        'user_id':fields.many2one('res.users', 'User', help='Logged in User who made the comment')
    }
    
    _defaults = {
        'date' : lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: