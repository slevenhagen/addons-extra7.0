# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2010 Verts Services India Pvt. Ltd.
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


{
    "name" : " Purchase double validation limit",
    "version" : "1.0",
    "author" : "Verts Team",
    "description" : """Sets default limit to 0 for purchase double validation""",
    "website"  : "http://www.verts.co.in",
    "depends"  : ['purchase_double_validation'],
    "category" : "Purchase",
    "init_xml" : [],
    "demo_xml" : [],
    "data"     : [
                  'purchase_double_validation_workflow_inherit.xml',
                  'purchase_view.xml'
                 ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate': '',
}
