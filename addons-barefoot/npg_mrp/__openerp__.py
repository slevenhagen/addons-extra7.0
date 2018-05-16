# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2015 NovaPoint Group INC (<http://www.novapointgroup.com>)
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
    'name': 'NPG Manufacture Resource Planning',
    'version': '1.0',
    'category': 'Manufacturing',
    'description': """
    This module adds customizations to import BOM data from csv files.
    Add enhancements for BOM list View Components
    """,
    'author': 'NovaPoint Group LLC',
    'website': ' http://www.novapointgroup.com',
    'depends': ['mrp_operations','procurement','npg_stock'],
    'data': ['wizard/wizard_bom_view.xml','view/mrp_view.xml','npg_mrp_workflow.xml'],
    'demo': [
    ],
    'css': ['static/src/css/npg.css',],
    'auto_install': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: