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
import openerp.addons.decimal_precision as dp

class change_standard_price(osv.TransientModel):
    _inherit = "stock.change.standard.price"
    _description = "Change Standard Price"
    _columns = {
        'new_price': fields.float('Price', required=True, digits_compute= dp.get_precision('Kpce Price'),
                                  help="If cost price is increased, stock variation account will be debited "
                                        "and stock output account will be credited with the value = (difference of amount * quantity available).\n"
                                        "If cost price is decreased, stock variation account will be creadited and stock input account will be debited."),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: