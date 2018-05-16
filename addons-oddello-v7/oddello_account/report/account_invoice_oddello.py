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

class oddello_inv_repo(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(oddello_inv_repo, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_address': self.get_address,
        })
    
    def get_address(self,add):
        invoice_adress = []
        invoice_adress.append(add.title or add.name or '')
        invoice_adress.append(add.street or '')
        invoice_adress.append(add.street2 or '')
        invoice_adress.append(add.zip or '')
        invoice_adress.append(add.city or '')
        invoice_adress.append(add.state_id.name or '')
        invoice_adress.append(add.country_id.name or '')
        return invoice_adress

report_sxw.report_sxw('report.account.invoice.oddello', 'account.invoice', 'addons/oddello_account/report/account_invoice_oddello.rml', parser=oddello_inv_repo, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
