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
{
    'name': 'Purchase Management',
    'version': '3.3',
    'category': 'Sales & Purchases',
    'description': """Modifications in Purchase Management
    """,
    'author': 'NovaPoint Group LLC',
    'website': 'http://www.novapointgroup.com',
    'depends': ['oddello_stock'],
    'data': [
             'security/security.xml',
             'purchase_view.xml', 
             'report/report_xml.xml',
             'stock_view.xml',
             'product_view.xml', 
             'purchasing_data.xml', 
             'partner_view.xml'
            ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: