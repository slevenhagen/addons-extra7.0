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
    'name':'CRM Claim Additions',
    'version':'1.05',
    'author':'NovaPoint Group LLC',
    'website':'http://www.novapointgroup.com',
    'category':'Generic Modules/CRM & SRM',
    'description':
    """
    This Module is an addition to the CRM Claim Module. This will extend the features of the claim relating
    the relevant products which are having some problems and are listed for claiming. This module helps you
    configure some basic problems of specific product category for e.g. if there is some issue with the a Camera,
    It may be lense failure or exhausted battery etc. It also allows you to track the product through its production lot.
    """,
    'depends':[
        'crm_claim',
        'stock',
    ],
    'data':[
        'security/crm_claim_security.xml',
        'security/ir.model.access.csv',
        'crm_claim_view.xml',
        'account_invoice.xml',
        'crm_sequence.xml'
    ],
    'test':[
        'test/crm_claim_additions_test.yml'
    ],
    'installable':True,
    'auto_install':False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: