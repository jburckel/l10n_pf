# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tahiti = fields.Char(string='TAHITI', size=6)
