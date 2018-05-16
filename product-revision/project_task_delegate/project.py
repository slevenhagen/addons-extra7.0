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
    
class project_task_delegate(orm.TransientModel):
    _inherit = "project.task.delegate"    

    _columns = {
        'name': fields.char('Delegated Title', size=128, required=True,
                            help="New title of the task delegated to the user"),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(project_task_delegate, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        task_pool = self.pool.get('project.task')
        task = task_pool.browse(cr, uid, record_id, context=context)
        task_name = task.name
        if 'project_id' in fields:
            res['project_id'] = int(task.project_id.id) if task.project_id else False
        if 'name' in fields:
            res['name'] = task_name + ' : Delegated'
        if 'planned_hours' in fields:
            res['planned_hours'] = 1.0
        if 'new_task_description' in fields:
            res['new_task_description'] = task.description
        return res

class project_task(orm.Model):
    _inherit = "project.task"    
    
    def _calc_global_hours(self, cr, uid, ids, fields_name, arg, context=None):
        result = {}
        for task in self.browse(cr, uid, ids, context=context):
            for field in fields_name:
                hours = 0.0
                if field == 'global_planned_hours':
                    hours = task.planned_hours
                    if task.child_ids:
                        for child in task.child_ids:
                            hours += child.planned_hours
                    result[task.id] = {
                        'global_planned_hours': hours,
                    }
                if field == 'global_remaining_hours':
                    hours = task.remaining_hours
                    if task.child_ids:
                        for child in task.child_ids:
                            hours += child.remaining_hours
                    result[task.id] = {
                        'global_remaining_hours': hours,
                    }
        return result
    
    _columns = {
        'global_planned_hours': fields.function(_calc_global_hours, string='Global Planned Hours', type='float', multi="planned_hours", store=False),
        'global_remaining_hours': fields.function(_calc_global_hours, string='Global Remaining Hours', type='float', multi="remaining_hours", store=False),
    }
    
    def do_delegate(self, cr, uid, ids, delegate_data=None, context=None):
        """
        Delegate Task to another users.
        """
        if delegate_data is None:
            delegate_data = {}
        assert delegate_data['user_id'], _("Delegated User should be specified")
        delegated_tasks = {}
        for task in self.browse(cr, uid, ids, context=context):
            delegated_task_id = self.copy(cr, uid, task.id, {
                'name': delegate_data['name'],
                'project_id': delegate_data['project_id'] and delegate_data['project_id'][0] or False,
                'user_id': delegate_data['user_id'] and delegate_data['user_id'][0] or False,
                'planned_hours': delegate_data['planned_hours'] or 0.0,
                'remaining_hours': delegate_data['planned_hours'] or 0.0,
                'parent_ids': [(6, 0, [task.id])],
                'description': delegate_data['new_task_description'] or '',
                'child_ids': [],
                'work_ids': []
            }, context=context)
            self._delegate_task_attachments(cr, uid, task.id, delegated_task_id, context=context)
            task.write({
                'remaining_hours': task.remaining_hours -  delegate_data['planned_hours'],
                'planned_hours': task.planned_hours -  delegate_data['planned_hours'],
            }, context=context)
            delegated_tasks[task.id] = delegated_task_id
        return delegated_tasks
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

