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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import time
from datetime import datetime


def get_data(self, cr, uid, ids, recordlist, data):
    
    account_period_obj = self.pool.get('account.period')
    bank_statements = []
    pointor = 0
    line_cursor = 0
    initial_lines = 2
    total_amount = 0
    bank_statement = {}
    bank_statement_lines = {}
    bank_statement["bank_statement_line"] = {}
    
    date_format = str(self.pool.get('account.bank.statement.import').browse(cr, uid, ids[0]).date_format)
    for line in recordlist:
        if line_cursor < initial_lines:
            line_cursor += 1
            continue
        line_splited = line.split(';')
        st_line = {}
        line_name = pointor
        if "Ancien solde" in line_splited[0]:
            balance_start = line_splited[4]
            if '.' in balance_start:
                balance_start = balance_start.replace('.','')
            if ' ' in balance_start:
                balance_start = balance_start.replace(' ','')
            if ',' in balance_start:
                balance_start = balance_start.replace(',','.')
            break
        st_line['date'] = time.strftime('%Y-%m-%d',time.strptime(line_splited[0], date_format))
        st_line['name'] = line_splited[1]
        amount = 0
        if line_splited[2]:
            amount = line_splited[2]
            st_line['account_id'] = data['payable_id'][0]
        if line_splited[3]:
            amount = line_splited[3]
            st_line['account_id'] = data['receivable_id'][0]
        # Format conversion
        if '.' in amount:
            amount = amount.replace('.','')
        if ' ' in amount:
            amount = amount.replace(' ','')
        if ',' in amount:
            amount = amount.replace(',','.')
        amount = float(amount or 0.0)
        if line_splited[2]:
            st_line['amount'] = - amount
        if line_splited[3]:
            st_line['amount'] = amount
        st_line['partner_id'] = False
        
        # check of uniqueness of a field in the data base
        date = st_line['date']
        check_ids = self.pool.get('account.bank.statement.line').search(cr,uid,[('name','=',line_splited[1]),('date','=',date),('amount','=',st_line['amount'])])
        if check_ids:
            continue        
        if not check_ids:   
            bank_statement_lines[line_name]=st_line
            line_name += 1                    
        bank_statement["bank_statement_line"] = bank_statement_lines
        pointor += 1
        print st_line
        total_amount += st_line['amount']

    # Saving data at month level
    bank_statement['balance_start'] = balance_start
    bank_statement['total_amount'] = total_amount
    bank_statement['journal_id'] = data['journal_id'][0]    
    period_id = account_period_obj.search(cr, uid, [('date_start', '<=', date), ('date_stop', '>=',date)])
    bank_statement['date'] = date
    bank_statement['period_id'] = period_id and period_id[0] or False
    bank_statements.append(bank_statement)
    print bank_statements
    return bank_statements

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: