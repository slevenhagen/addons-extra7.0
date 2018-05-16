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
from openerp.report import report_sxw

class report_bill_lading(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_bill_lading, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'net_weight': self.net_weight,
        })

    def net_weight(self, line):
        return line.product_id.weight * line.product_qty

class report_bill_lading_master(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_bill_lading_master, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'net_weight': self.net_weight,
            'get_type': self._get_type,
        })

    def _get_type(self, obj):
        if type(obj) == unicode:
            return False
        return True

    def net_weight(self, line):
        return line.product_id.weight * line.product_qty

    def set_context(self, objects, data, ids, report_type=None):
        objects = data['objects']
        return super(report_bill_lading_master, self).set_context(objects, data, ids, report_type)


report_sxw.report_sxw('report.webkit.bill.lading2',
                       'stock.picking.out',
                       'addons/oddello_stock/reports/report_webkit_lading.mako',
                       parser=report_bill_lading)

report_sxw.report_sxw('report.webkit.master.bill.lading',
                       'stock.picking.out',
                       'addons/oddello_stock/reports/report_webkit_master_lading.mako',
                       parser=report_bill_lading_master)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: