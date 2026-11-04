# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    tahiti = fields.Char(
        related='partner_id.tahiti', string='TAHITI',
        help="TAHITI number of the company, read from its tax identifier.")
    cps = fields.Char(string='CPS', size=8)
    ape = fields.Char(string='APE', size=5)

    l10n_pf_rounding_difference_loss_account_id = fields.Many2one('account.account', check_company=True)
    l10n_pf_rounding_difference_profit_account_id = fields.Many2one('account.account', check_company=True)
