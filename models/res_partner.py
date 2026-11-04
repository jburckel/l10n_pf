# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # In French Polynesia the TAHITI number is the business identifier and
    # serves as the tax identifier: there is no separate VAT number. The
    # number is therefore stored once, in the standard ``vat`` field (printed
    # on invoices, used by imports and autocompletion), and exposed here for
    # the Polynesian partners only, normalized (no spaces, no "PF" prefix).
    tahiti = fields.Char(
        string='TAHITI', compute='_compute_tahiti',
        help="TAHITI number of a Polynesian partner, read from its tax "
             "identifier. Empty for partners of another country, whose tax "
             "identifier is a foreign VAT number.")

    @api.depends('vat', 'country_id')
    def _compute_tahiti(self):
        for partner in self:
            partner.tahiti = self._l10n_pf_tahiti_from_vat(
                partner.vat, partner.country_id)

    @api.model
    def _l10n_pf_tahiti_from_vat(self, vat, country):
        """TAHITI number carried by a tax identifier, or ``False`` when the
        partner belongs to another country or has no identifier."""
        if country and country.code != 'PF':
            return False
        number = re.sub(r'[\s.\-]', '', vat or '').upper()
        if number.startswith('PF') and len(number) > 2:
            number = number[2:]
        return number or False
