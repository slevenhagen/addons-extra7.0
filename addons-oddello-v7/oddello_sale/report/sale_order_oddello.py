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
import time
from openerp.report import report_sxw

class oddello_so(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(oddello_so, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
        
report_sxw.report_sxw('report.sale.order.oddello', 'sale.order', 'addons/oddello_sale/report/sale_order_oddello.rml', parser=oddello_so, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

