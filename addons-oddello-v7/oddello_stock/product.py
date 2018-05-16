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

from openerp.osv import osv, fields

class hu_type(osv.Model):
    _name = 'hu.type'
    _description = "HU Type"

    _columns = {
        'name': fields.char('HU Type', size=128),
    }

class product_packaging(osv.Model):
    _inherit = "product.packaging"
    _columns = {
        'hu_type_id' : fields.many2one('hu.type', 'HU Type', required=True),
    }

    def _get_1st_hu(self, cr, uid, context=None):
        cr.execute('select id from hu_type order by id asc limit 1')
        res = cr.fetchone()
        return (res and res[0]) or False

    _defaults = {
        'hu_type_id' :_get_1st_hu,
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for pckg in self.browse(cr, uid, ids, context=context):
            p_name = pckg.ean and '[' + pckg.ean + '] ' or ''
            p_name += pckg.hu_type_id.name
            res.append((pckg.id, p_name))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
