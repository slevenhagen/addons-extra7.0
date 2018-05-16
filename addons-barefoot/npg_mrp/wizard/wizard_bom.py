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

from openerp.osv import osv, fields
import csv
import cStringIO
import base64
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class bom_read_csv(osv.osv_memory):
    _name = 'bom.read.csv'
    _columns = {
        'browse_path': fields.binary('Csv File Path'),
    }

    def import_csv(self, cr, uid, ids, context=None):
        bom_obj = self.pool.get('mrp.bom')
        prod_obj = self.pool.get('product.product')
        if context is None:
            context = {}
        for wiz_rec in self.browse(cr, uid, ids, context=context):
            bom_vals = {}
            str_data = base64.decodestring(wiz_rec.browse_path)
            if not str_data:
                raise osv.except_osv('Warning', 'The file contains no data')
            try:
                bom_data = list(csv.reader(cStringIO.StringIO(str_data)))
            except:
                raise osv.except_osv('Warning', 'Make sure you saved the file as .csv extension and import!')
            
            headers_list = []
            for header in bom_data[0]:
                headers_list.append(header.strip())
            headers_dict = {
                'parent': headers_list.index('Parent'),
                'child': headers_list.index("Child"),
                'qty': headers_list.index('Qty'),
            }
            
            for data in bom_data[1:]:
                parent = data[headers_dict['parent']]
                child = data[headers_dict['child']]
                qty = data[headers_dict['qty']]
                if parent in bom_vals:
                    bom_vals[parent].append((child, qty))
                else:
                    bom_vals.update({parent: [(child, qty)]})
            for key, vals in bom_vals.iteritems():
                parent_prod_ids = prod_obj.search(cr, uid, [('default_code', '=', key)], context=context)
                if not parent_prod_ids:
                    _logger.info('Error', key +' Default Code is not available')
                    raise osv.except_osv('Error', key +' Default Code is not available')
                parent_product = prod_obj.browse(cr, uid, parent_prod_ids, context=context)
                child_list = []
                product_onchange_dict = {}
                for val in vals:
                    child_prod_ids = prod_obj.search(cr, uid, [('default_code', '=', val[0])], context=context)
                    child_product = prod_obj.browse(cr, uid, child_prod_ids, context=context)
                    product_onchange_dict = bom_obj.onchange_product_id(cr, uid, [], child_prod_ids[0], parent_product[0].name, context=context)['value']
                    child_list.append((0, 0, {'product_id': child_prod_ids[0], 'product_uom': child_product[0].uom_id.id, 'product_qty': val[1]}))
                if product_onchange_dict:
                    bom_id = bom_obj.create(cr, uid, {'product_id': parent_prod_ids[0], 'name': parent_product[0].name, 'product_uom': product_onchange_dict.values()[1], 'bom_lines': child_list}, context=context)
                    _logger.info('BOM  # %s created for Product %s',bom_id,parent_product[0].name)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: