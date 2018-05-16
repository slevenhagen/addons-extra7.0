# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2013 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from osv import osv,fields
from tools.translate import _
import threading
import time
import netsvc

from sql_db import db_connect
import pooler
import base64

class Deferred(threading.Thread):
    def __init__(self, dbname, uid, process_id):
        threading.Thread.__init__(self)
        self._process_id = process_id
        self._ids = []
        self._total = 0.0
        self._processed_ids = []
        self._processed = 0.0
        self._progress = 0.0
        self._intercept_value = 1.0
        self._state = 'start'
        self._start_time = None
        self._time_elapsed = 0.0
        self._time_left = 0.0
        self._speed = 0.0

        self.method = None
        self.args = []
        self.kwargs = {}

        self.result = None
        self._result_parser = "result[0]"
        self.dbname = dbname
        self.uid = uid

    def run(self):
        cr = db_connect(self.dbname).cursor()
        pool = pooler.get_pool(cr.dbname)
        deferred_obj = pool.get('deferred_processing.task')
        self._start_time = time.time()
        deferred_obj.write(cr, self.uid, self._process_id, {'state':'process'})
        cr.commit()
        self._state = 'process'
        if 'context' in self.kwargs:
            self.kwargs['context'].update({'deferred_process':self})
        else:
            self.args[-1].update({'deferred_process':self}) 
        if self.kwargs:
            self.result = apply(self.method, (cr,self.uid)+self.args, self.kwargs)
        else:
            self.result = apply(self.method, (cr,self.uid)+self.args)
        
        self.refresh_status()
        self.get_speed()
        self._state = 'done'
        self._processed = self._total
        self._progress = 100.0
        to_write = {'state':'done'}
        if self.result and type(self.result)!=bool:
            if self._result_parser:
                self.result = eval(self._result_parser, {}, {'result':self.result})
                to_write['result'] = base64.encodestring(self.result)
        cr.rollback()
        deferred_obj.write(cr, self.uid, self._process_id, to_write)
        cr.commit()
        cr.close()

    def progress_update(self, rate=1):
        if self._processed<self._total:
            self._processed += 1
        if rate>1:rate = 1
        self._progress += rate*self._intercept_value
        return self._progress

    def get_progress(self):
        return self._progress

    def refresh_status(self):
        if self._start_time and self._state!='done':
            self._time_elapsed = time.time() - self._start_time
            if self._processed:
                self._time_left = (self._time_elapsed / self._processed) * (self._total - self._processed)
        return {'time_elapsed': self._time_elapsed, 'time_left':self._time_left, 'state':self._state}

    def get_speed(self):
        self._speed = self._processed and self._time_elapsed / self._processed or False
        return self._speed

    def set_total_items(self, ids):
        self._ids = ids
        self._total = len(ids)
        self._intercept_value = 100.0/self._total

    def get_processed(self):
        return self._processed

    def get_total(self):
        return self._total

    def get_state(self):
        return self._state

class deferred_processing_task(osv.osv):
    _name = 'deferred_processing.task'

    def __init__(self, pool, cr):
        super(deferred_processing_task, self).__init__(pool, cr)
        self._processed = {}

    def new_process(self, cr, uid, process_id, context={}):
        deferred = Deferred(cr.dbname, uid, process_id)
        self._processed[process_id] = deferred
        return deferred

    def start_process_report(self, cr, uid, process_id, ids, report_id, context={}):
        deferred = self._processed[process_id]
        deferred.set_total_items(ids)
        context['active_ids'] = ids
        report = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_id, context=context)
        data = {'model':  report.model, 'id': context['active_ids'][0], 'report_type': 'aeroo'}
        deferred.method = netsvc.Service._services['report.%s' % report.report_name].create
        #context.update({'deferred_process_id':process_id})
        deferred.args = (context['active_ids'], data, context)
        cr.commit()
        deferred.start()
        return True

    def start_process_object(self, cr, uid, process_id, model, method, ids, args, kwargs={}):
        obj = self.pool.get(model)
        deferred = self._processed[process_id]
        deferred.set_total_items(ids)
        deferred.method = getattr(obj, method)
        deferred.args = args
        deferred.kwargs = kwargs
        deferred.start()
        return True

    def update_process(self, process_id, ids):
        deferred = self._processed[process_id]
        #deferred.update_processed(len(ids))
        #deferred.update_time()
        return True

    def _get_progress(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for curr_id in ids:
            deferred = self._processed.get(curr_id)
            if deferred:
                progress = deferred.get_progress()
                total = deferred.get_total()
                state = deferred.get_state()
                if total==0:
                    result[curr_id] = 0.0
                else:
                    if progress>=100.0 and state=='process':
                        result[curr_id] = 99.99
                    else:
                        result[curr_id] = progress
            else:
                result[curr_id] = 0.0
        return result

    def _get_time(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for curr_id in ids:
            result[curr_id] = {}
            deferred = self._processed.get(curr_id)
            if deferred:
                res = deferred.refresh_status()
                result[curr_id]['time_left'] = res['time_left'] / 60
                result[curr_id]['time_elapsed'] = res['time_elapsed'] / 60
            else:
                result[curr_id]['time_left'] = 0.0
                result[curr_id]['time_elapsed'] = 0.0
        return result

    def _get_speed(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for curr_id in ids:
            deferred = self._processed.get(curr_id)
            result[curr_id] = deferred and deferred.get_speed() or 0.0
        return result

    def _get_total(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for curr_id in ids:
            deferred = self._processed.get(curr_id)
            result[curr_id] = deferred and int(deferred.get_total()) or 0
        return result

    def _get_processed(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for curr_id in ids:
            deferred = self._processed.get(curr_id)
            result[curr_id] = deferred and int(deferred.get_processed()) or 0
        return result

    def refresh_status(self, cr, uid, ids, context=None):
        rec = self.read(cr, uid, ids[0], ['state'], context=context)
        if rec['state']=='process':
            self.write(cr, uid, ids, {}, context=context)
        return True

    def create(self, cr, uid, vals, context={}):
        if not vals.get('user_id'):
            vals['user_id'] = uid
        res_id = super(deferred_processing_task, self).create(cr, uid, vals, context)
        return res_id

    _columns = {
        'state': fields.selection([('start','To Start'),
('process','In Progress'),
('interrupt','Interrupted'),
('done','Done'),], 'State', size=64, required=False, readonly=False, translate=False, help=''),
        'progress': fields.function(_get_progress, type='float', method=True, store=True, string='Progress', help=''),
        'time_left': fields.function(_get_time, type='float', method=True, store=True, string='Time Left', multi='time', help='Estimated time left.'),
        'time_elapsed': fields.function(_get_time, type='float', method=True, store=True, string='Time Elapsed', multi='time', help=''),
        'speed': fields.function(_get_speed, type='float', method=True, store=True, string='Sec. per Entry', help='Average number of seconds per entry.'),
        'total': fields.function(_get_total, type='integer', method=True, store=True, string='Total Entries', help='Number of entries to be processed.'),
        'processed': fields.function(_get_processed, type='integer', method=True, store=True, string='Processed Entries', help='Number of processed entries so far.'),
        'result': fields.binary('Result Data', required=False, readonly=False, help=''),
        'user_id': fields.many2one('res.users', 'User', domain="[]", ondelete='set null', required=True, readonly=False, help=''),
        'name': fields.char('Name', size=64, required=True, readonly=True, translate=False, help=''),
    }

    _defaults = {
        'state': 'start',
        'user_id': 1,
    }

