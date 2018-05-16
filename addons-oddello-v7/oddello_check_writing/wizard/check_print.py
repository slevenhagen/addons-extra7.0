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


# class print_check(osv.TransientModel):
#     """
#     Check Printing
#     """
#     _inherit = "print.check"
# 
#     def check_option(self, cr, uid, ids, context=None):
#         """
#         Function to check the option if check is already printed
#         """
#         if context is None:
#             context = {}
#         data = self.browse(cr, uid, ids[0], context=context)
#         if data.print_new:
#             msg =  'What happened to the existing check no ' + str(data.preprint_msg.split(':\n')[1]).replace('\n', ', ') + '?'
#             self.write(cr, uid, ids, {'preprint_msg': msg, 'state': 'reprint_new'}, context=context)
#         elif data.reprint:
#             company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
#             if company_obj.check_layout == 'top':
#                 report_name = 'account.print.check.top.oddello'
#             if company_obj.check_layout == 'middle':
#                 report_name = 'account.print.check.middle'
#             if company_obj.check_layout == 'bottom':
#                 report_name = 'account.print.check.bottom'
# 
#             return {
#             'type': 'ir.actions.report.xml',
#             'report_name': report_name,
#             'datas': {
#                 'model': 'account.voucher',
#                 'id': context.get('active_ids', False) and context['active_ids'][0],
#                 'ids': context.get('active_ids', []),
#                 'report_type': 'pdf'
#                 },
#             'nodestroy': False
#             }
#         elif data.update_check_no:
#             msg =  'What happened to the existing check no ' + str(data.preprint_msg.split(':\n')[1]).replace('\n', ', ') + '?'
#             self.write(cr, uid, ids, {'preprint_msg': msg, 'state': 'update_check_no'}, context=context)
#         return {'nodestroy': True}
# 
# 
#     def print_check(self, cr, uid, ids, context=None):
#         """
#         Function to print check
#         """
#         if context is None:
#             context = {}
# 
#         if not context.get('active_ids'):
#             return []
# 
#         seq = {}
#         checks = []
#         journals = []
#         voucher_objs = self.pool.get('account.voucher').browse(cr, uid, context['active_ids'], context=context)
#         chck_obj = self.pool.get('check.log')
#         data = self.browse(cr, uid, ids[0], context=context)
#         #FIXME: Please check whether we need 3 loops here.
#         for voucher in voucher_objs:
#             if voucher.journal_id.check_sequence:
#                 seq[voucher.journal_id.check_sequence.id] = True
#             else:
#                 raise wizard.except_wizard(_('Warning'), _('Please add "Check Sequence" for journal %s.'%str(voucher.journal_id.name)))
#         for seq_id in seq:
#             #FIXME: Please check whether this call is necessary
#             nxt_no = self.pool.get('ir.sequence').read(cr, uid, seq_id, ['number_next'], context=context)['number_next']
#             self.pool.get('ir.sequence').write(cr, uid, [seq_id], {'number_next': data.new_no}, context=context)
# 
#         for voucher in voucher_objs:
#             chck_log_ids = chck_obj.search(cr, uid, [('check_no','=',data.new_no), ('journal_id','=',voucher.journal_id.id)], context=context)
#             if chck_log_ids:
#                 raise osv.except_osv(_('Error !'), _('The check number %s has been already printed for the journal %s.') % (data.new_no,voucher.journal_id.name))
#             else: 
#                 next_seq = self.pool.get('ir.sequence').get_id(cr, uid, voucher.journal_id.check_sequence.id, test='id', context=context)
#                 self.pool.get('account.voucher').write(cr, uid, [voucher.id],{'chk_seq': next_seq, 'chk_status': True}, context=context)
#                 self.pool.get('check.log').create(cr, uid, {'name': voucher.id, 'status': 'active', 'check_no': next_seq,'journal_id':voucher.journal_id.id}, context=context)
# 
#         if data.state == 'print':
#             company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
#             if company_obj.check_layout == 'top':
#                 report_name = 'account.print.check.top.oddello'
#             if company_obj.check_layout == 'middle':
#                 report_name = 'account.print.check.middle'
#             if company_obj.check_layout == 'bottom':
#                 report_name = 'account.print.check.bottom'
#             return {
#                 'type': 'ir.actions.report.xml',
#                 'report_name': report_name,
#                 'datas': {
#                     'model': 'account.voucher',
#                     'id': context.get('active_ids', False) and context.get('active_ids')[0],
#                     'ids': context.get('active_ids', []),
#                     'report_type': 'pdf'
#                     },
#                 'nodestroy': False
#                 }
#         else:
#             return {}
# 
# print_check()

class account_check_write(osv.TransientModel):
    _inherit = 'account.check.write'
    _description = 'Print Check in Batch'

#    def print_check_write(self, cr, uid, ids, context=None):
#        
#        if context is None:
#            context = {}
#        voucher_obj = self.pool.get('account.voucher')
#        ir_sequence_obj = self.pool.get('ir.sequence')
#
#        #update the sequence to number the checks from the value encoded in the wizard
#        dummy, sequence_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_check_writing', 'sequence_check_number')
#        increment = ir_sequence_obj.read(cr, uid, sequence_id, ['number_increment'])['number_increment']
#        new_value = self.browse(cr, uid, ids[0], context=context).check_number
#        ir_sequence_obj.write(cr, uid, sequence_id, {'number_next': new_value})
#
#        #validate the checks so that they get a number
#        voucher_ids = context.get('active_ids', [])
#        for check in voucher_obj.browse(cr, uid, voucher_ids, context=context):
#            new_value += increment
#            if check.number:
#                raise osv.except_osv(_('Error!'),_("One of the printed check already got a number."))
#        voucher_obj.proforma_voucher(cr, uid, voucher_ids, context=context)
#
#        #update the sequence again (because the assignation using next_val was made during the same transaction of
#        #the first update of sequence)
#        ir_sequence_obj.write(cr, uid, sequence_id, {'number_next': new_value})
#
#        #print the checks
#        check_layout_report = {
#            'top' : 'account.print.check.top.oddello',
#            'middle' : 'account.print.check.middle',
#            'bottom' : 'account.print.check.bottom',
#        }
#        check_layout = voucher_obj.browse(cr, uid, voucher_ids[0], context=context).company_id.check_layout
#        if not check_layout:
#            check_layout = 'top'
#        return {
#            'type': 'ir.actions.report.xml', 
#            'report_name':check_layout_report[check_layout],
#            'datas': {
#                'model':'account.voucher',
#                'ids': voucher_ids,
#                'report_type': 'pdf'
#                },
#            'nodestroy': True
#            }
#        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: