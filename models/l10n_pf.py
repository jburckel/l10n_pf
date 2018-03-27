# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    tahiti = fields.Char(string='TAHITI', size=6)
    cps = fields.Char(string='CPS', size=8)
    ape = fields.Char(string='APE', size=5)
