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

from openerp.osv import osv, fields
from openerp import netsvc


class  crm_rma_line(osv.Model):
    _inherit='crm.rma.line'
    _columns={
              'product_note': fields.text('Notes',size=128,readonly=True)
              }

class crm_rma(osv.Model):

    def get_web_details(self, cr, uid, vals):
        rma_vals ={}
        partner_id = self.pool.get('res.partner').search(cr,uid,[('name','=','RMA Pending')])

        partner_shipping_id = self.pool.get('res.partner.address').search(cr,uid,[('partner_id','=',partner_id)])
        contact_state_id = False
        if vals['contact_state']:
            contact_state_ids = self.pool.get('res.country.state').search(cr,uid,[('code','=',vals['contact_state'])])
            contact_state_id = contact_state_ids and contact_state_ids[0] or False
#        shipping_state_id = self.pool.get('res.country.state').search(cr,uid,[('code','=',vals['shipping_state'])])
        rma_vals = {
                'partner_id' : partner_id[0],
                'partner_shipping_id' : partner_shipping_id[0],
                'contact_company_name' : vals['contact_company_name'],
                'contact_address' : vals['contact_address'],
                'contact_name' : vals['contact_name'],
                'contact_city' : vals['contact_city'],
                'contact_state_id' : contact_state_id,
                'contact_zip' : vals['contact_zip'],
                'contact_phone' : vals['contact_phone'],
                'contact_fax' : vals['contact_fax'],
                'contact_email' : vals['contact_email'],
                'comments':vals['additional_comments'],
#                'shipping_company_name' : vals['shipping_company_name'],
#                'shipping_name' : vals['shipping_name'],
#                'shipping_address' : vals['shipping_address'],
#                'shipping_city' : vals['shipping_city'],
#                'shipping_state_id' : shipping_state_id and shipping_state_id[0] or False,
#                'shipping_zip' : vals['shipping_zip'],
#                'shipping_phone' : vals['shipping_phone'],
#                'shipping_fax' : vals['shipping_fax'],
#                'shipping_email' :vals['shipping_email'],

            }
        if vals['same_as_contact']:
            rma_vals.update({'same_as_contact':True})



        serials ={}
        models ={}
        reason ={}
	req_proc = {}
	limit = int(vals['limit'])
        for i in range(1, limit+1):
            serials[i]= vals['serial_'+str(i)]
            models[i] = vals['model_'+str(i)]
            reason[i] = vals['reason_'+str(i)]
	    req_proc[i] = vals['requested_procedure_' + str(i)]
        #for i in range(1, limit+1):
        #    if not models[i]:
        #      models.pop(i)
        if models.keys():
            rma_id = self.pool.get('crm.rma').create(cr,uid,rma_vals)
        lot_pool = self.pool.get('stock.production.lot')
        product_pool = self.pool.get('product.product')
        for serial in models.keys():
                lot_ids = lot_pool.search(cr,uid,[('name','=',serials[serial])])
                lot_id = lot_ids and lot_ids[0] or False
#                if lot_id:
#                    product_id = lot_pool.browse(cr,uid,lot_id[0]).product_id.id
#                    product_uom = lot_pool.browse(cr,uid,lot_id[0]).product_id.uom_id.id
#
#                    vals = {
#                        'product_lot_id':lot_id[0],
#                        'product_id':product_id,
#                        'product_uom':product_uom,
#                        'product_qty':1,
#                        'rma_id':rma_id,
#                        'name':reason[serial]
#                        }
                product_id = product_pool.search(cr,uid,[('default_code','=',models[serial])])
                if product_id:
                        product_uom = product_pool.browse(cr,uid,product_id[0]).uom_id.id

                        vals = {
                                'product_lot_id':lot_id,
                                'product_id':product_id[0],
                                'product_uom':product_uom,
                                'product_qty':1,
                                'rma_id':rma_id,
                                'name':reason[serial],
				'requested_procedure': req_proc[serial]
                                }
                else:
                        product_id = product_pool.search(cr,uid,[('default_code','=','RMA')])
                        product_uom = product_pool.browse(cr,uid,product_id[0]).uom_id.id
                        note = "Model %s not Found"%models[serial]
                        vals = {
                                'product_lot_id':lot_id,
                                'product_id':product_id[0],
                                'product_uom':product_uom,
                                'product_qty':1,
                                'rma_id':rma_id,
                                'name':reason[serial],
                                'product_note' : note,
				'requested_procedure': req_proc[serial],
                                }

                self.pool.get('crm.rma.line').create(cr,uid,vals)
        return True

    _inherit='crm.rma'
    _columns = {
        'contact_company_name' : fields.char('Company Name',size=64),
        'contact_address' : fields.char('Address',size=64),
        'contact_name' : fields.char('Name',size=64),
        'contact_city' : fields.char('City',size=64),
        'contact_state_id' :fields.many2one('res.country.state','State'),
        'contact_zip' : fields.char('Zip',size=64),
        'contact_phone': fields.char('Phone',size=64),
        'contact_fax': fields.char('Fax',size=64),
        'contact_email' :fields.char('Email',size=64),
        'shipping_company_name' : fields.char('Company Name',size=64),
        'shipping_address' : fields.char('Address',size=64),
        'shipping_name' : fields.char('Name',size=64),
        'shipping_city' : fields.char('City',size=64),
        'shipping_state_id' :fields.many2one('res.country.state','State'),
        'shipping_zip' : fields.char('Zip',size=64),
        'shipping_phone': fields.char('Phone',size=64),
        'shipping_fax': fields.char('Fax',size=64),
        'shipping_email' :fields.char('Email',size=64),
        'same_as_contact' : fields.boolean('Same As Contact Address?'),
        'comments': fields.text('Additional Comments',size=128)
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: