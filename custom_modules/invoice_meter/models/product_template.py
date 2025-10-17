# models/product_template.py
# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_metered_product = fields.Boolean(
        string='Metered Product',
        default=False,
        help='Check this for products that require meter readings (water, electricity, gas, etc.)'
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_metered_product = fields.Boolean(
        related='product_tmpl_id.is_metered_product',
        store=True,
        readonly=True
    )