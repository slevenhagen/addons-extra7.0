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
import base64
import sys, StringIO
import os
from openerp.tools.translate import _

class stock_picking(osv.Model):
    _inherit = 'stock.picking'
    _columns = {
        'pod_scan_num' : fields.char('POD Attach Num', size=32),
        'promise_date_po' : fields.related("purchase_id", "promise_date", type="date", string="Promised Date"),
    }

class stock_picking_out(osv.Model):
    _inherit = 'stock.picking.out'
    _columns = {
        'pod_scan_num' : fields.char('POD Attach Num', size=32),
        'promise_date_po' : fields.related("purchase_id", "promise_date", type="date", string="Promised Date"),
    }

    def link_file(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_attachment_pool = self.pool.get('ir.attachment')

        for rec in self.browse(cr, uid, ids, context=None):
            if rec.pod_scan_num:
                attach_ids = ir_attachment_pool.search(cr, uid, [('res_model','=','stock.picking.out'), ('res_id','=',rec.id), ('name','=','pod_' + str(rec.pod_scan_num) + '.pdf')], context=context)
                if not attach_ids:
                    try:
                        directory_path = '/home/pod_scan/'
                        value = file(directory_path + rec.pod_scan_num + '.pdf').read()
                        result = base64.encodestring(value)
                        vals = {'name' : 'pod_' + str(rec.pod_scan_num) + '.pdf',
                                'datas_fname' : 'pod_' + str(rec.pod_scan_num) + '.pdf',
                                'datas' : result,
                                'res_model' : 'stock.picking.out',
                                'res_id' : rec.id
                                }
                        attach_id = ir_attachment_pool.create(cr, uid, vals, context=context)
                    except IOError:
                        raise osv.except_osv(_('File Error'), _(str(rec.pod_scan_num) + '.pdf not Found !'))
        return True


class stock_picking_in(osv.Model):
    _inherit = 'stock.picking.in'
    _columns = {
        'pod_scan_num' : fields.char('POD Attach Num', size=32),
        'promise_date_po' : fields.related("purchase_id", "promise_date", type="date", string="Promised Date"),
    }

    def link_file(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_attachment_pool = self.pool.get('ir.attachment')

        for rec in self.browse(cr, uid, ids, context=None):
            if rec.pod_scan_num:
                attach_ids = ir_attachment_pool.search(cr, uid, [('res_model','=','stock.picking.in'), ('res_id','=',rec.id), ('name','=','pod_' + str(rec.pod_scan_num) + '.pdf')], context=context)
                if not attach_ids:
                    try:
                        directory_path = '/home/pod_scan/'
                        value = file(directory_path + rec.pod_scan_num + '.pdf').read()
                        result = base64.encodestring(value)
                        vals = {'name' : 'pod_' + str(rec.pod_scan_num) + '.pdf',
                                    'datas_fname' : 'pod_' + str(rec.pod_scan_num) + '.pdf',
                                    'datas' : result,
                                    'res_model' : 'stock.picking.in',
                                    'res_id' : rec.id
                                    }
                        attach_id = ir_attachment_pool.create(cr, uid, vals, context=context)
                        if attach_id:
                            self.write(cr, uid, [rec.id], {'attached_truck_driver_signature' : True}, context=context)
                    except IOError:
                        raise osv.except_osv(_('File Error'), _(str(rec.pod_scan_num) + '.pdf not Found !'))
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
