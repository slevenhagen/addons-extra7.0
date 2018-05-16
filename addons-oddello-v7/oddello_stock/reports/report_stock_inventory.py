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

from osv import fields, osv
import tools

class report_stock_inventory(osv.osv):
    _inherit = "report.stock.inventory"
    
    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        if context is None:
            context = {}
        res = super(report_stock_inventory, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby)
        for rec in res:
            if rec['product_qty'] < 0:
                rec['product_qty'] = rec['value'] = 0.0 
        return res

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_stock_inventory')
        cr.execute("""
CREATE OR REPLACE view report_stock_inventory AS (
    (SELECT
        min(m.id) as id, m.date as date,
        m.partner_id as partner_id, m.location_id as location_id,
        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type,
        m.company_id,
        m.state as state, m.prodlot_id as prodlot_id,
        coalesce(sum(-pt.standard_price * m.product_qty * pu.factor / u.factor)::decimal, 0.0) as value,
        CASE when pt.uom_id = m.product_uom
        THEN
        coalesce(sum(-m.product_qty)::decimal, 0.0)
        ELSE
        coalesce(sum(-m.product_qty * pu.factor / u.factor )::decimal, 0.0) END as product_qty
    FROM
        stock_move m
            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
            LEFT JOIN product_product pp ON (m.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
            LEFT JOIN product_uom u ON (m.product_uom=u.id)
            LEFT JOIN stock_location l ON (m.location_id=l.id)
        where pt.sale_ok = 't'
    GROUP BY
        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id,  m.location_dest_id,
        m.prodlot_id, m.date, m.state, l.usage, m.company_id,pt.uom_id
) UNION ALL (
    SELECT
        -m.id as id, m.date as date,
        m.partner_id as partner_id, m.location_dest_id as location_id,
        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type,
        m.company_id,
        m.state as state, m.prodlot_id as prodlot_id,
        coalesce(sum(pt.standard_price * m.product_qty * pu.factor / u.factor )::decimal, 0.0) as value,
        CASE when pt.uom_id = m.product_uom
        THEN
        coalesce(sum(m.product_qty)::decimal, 0.0)
        ELSE
        coalesce(sum(m.product_qty * pu.factor / u.factor)::decimal, 0.0) END as product_qty
    FROM
        stock_move m
            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
            LEFT JOIN product_product pp ON (m.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
            LEFT JOIN product_uom u ON (m.product_uom=u.id)
            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
     where pt.sale_ok = 't'
    GROUP BY
        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id, m.location_dest_id,
        m.prodlot_id, m.date, m.state, l.usage, m.company_id,pt.uom_id
    )
);
        """)
report_stock_inventory()