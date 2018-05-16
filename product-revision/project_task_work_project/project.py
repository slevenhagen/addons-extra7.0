# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
     
class project_work(orm.Model):
    _inherit = "project.task.work"
    _columns = {
        'project_id': fields.related('task_id', 'project_id', string='Project', type='many2one', relation='project.project', readonly=True),
    }
    
class project_task(orm.Model):
    _inherit = "project.task"
    
    def name_get(self, cr, user, ids, context=None):
        
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        
        def _name_get(d):
            name = d.get('name','')
            project_name = d.get('project_name',False)
            if project_name:
                name = '[%s] %s' % (project_name,name)
            return (d['id'], name)

        result = []
        for task in self.browse(cr, user, ids, context=context):
            mydict = {
                      'id': task.id,
                      'name': task.name,
                      'project_name': False,
                      }
            if task.project_id:
                mydict.update({'project_name':task.project_id.name})
            result.append(_name_get(mydict))
        return result
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            project_ids = self.pool.get('project.project').search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            ids = self.search(cr, user, [('project_id','in',project_ids)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

