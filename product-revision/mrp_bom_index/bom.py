# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from openerp import tools
from openerp.tools.translate import _
import re

class mrp_bom(orm.Model):
    _inherit = 'mrp.bom'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids,
                          ['name','revision_index'],
                          context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['revision_index']:
                name += ' [' + record['revision_index'] + ']'
            res.append((record['id'], name))
        return res

    def name_search(self, cr, user, name='', args=None,
                    operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('revision_index', '=', name)]+ args,
                              limit=limit, context=context)
            if not ids:
                # Do not merge the 2 next lines into one single search,
                # SQL search performance would be abysmal
                # on a database with thousands of matching products,
                # due to the huge merge+unique needed for the OR operator
                # (and given the fact that the 'name'
                # lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python
                # will give much better performance
                ids = set()
                ids.update(self.\
                           search(cr, user,
                                  args + [('revision_index', operator, name)],
                                  limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes
                    # in the results, that's fine
                    new_limit = (limit and (limit-len(ids)) or False)
                    ids.update(self.\
                               search(cr, user,
                                      args + [('name', operator, name)],
                                      limit=new_limit, context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.\
                        search(cr, user,
                               [('revision_index','=', res.group(2))] + args,
                               limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    _columns = {
        'revision_index': fields.char('Revision index', size=32),
    }

    _defaults = {
        'revision_index': "A",
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
