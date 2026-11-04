# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import TransactionCase, tagged


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestTahiti(TransactionCase):

    def test_tahiti_from_vat(self):
        Partner = self.env['res.partner']
        pf = self.env.ref('base.pf')
        partner = Partner.create({'name': 'Perles Moana', 'country_id': pf.id})
        self.assertFalse(partner.tahiti)
        partner.vat = '123456'
        self.assertEqual(partner.tahiti, '123456')
        # Normalized: spaces, dots and the "PF" prefix are dropped.
        partner.vat = ' pf a12 345 '
        self.assertEqual(partner.tahiti, 'A12345')
        # No country: assumed Polynesian.
        partner.country_id = False
        self.assertEqual(partner.tahiti, 'A12345')
        # A foreign partner carries a VAT number, not a TAHITI number.
        partner.write({'country_id': self.env.ref('base.nc').id, 'vat': 'NC123456'})
        self.assertFalse(partner.tahiti)

    def test_company_tahiti_follows_partner(self):
        company = self.env['res.company'].create({
            'name': 'Fare Poerava Test',
            'country_id': self.env.ref('base.pf').id,
        })
        company.vat = 'B98765'
        self.assertEqual(company.partner_id.vat, 'B98765')
        self.assertEqual(company.tahiti, 'B98765')

    def test_vat_label(self):
        self.assertEqual(self.env.ref('base.pf').vat_label, 'TAHITI')
