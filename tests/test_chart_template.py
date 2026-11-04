# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestChartTemplatePF(AccountTestInvoicingCommon):

    @classmethod
    @AccountTestInvoicingCommon.setup_chart_template('pf')
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data['company']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Client Papeete',
            'country_id': cls.env.ref('base.pf').id,
        })

    def _tax(self, xmlid):
        return self.env['account.chart.template'].with_company(self.company).ref(xmlid)

    def _box(self, moves, tag_name, sign=1):
        """Amount of a tax report box fed by ``tag_name``, with the sign of
        its formula (``-A01`` for sales, ``C11`` for purchases)."""
        lines = moves.line_ids.filtered(
            lambda l: tag_name in l.tax_tag_ids.mapped('name'))
        return sign * sum(lines.mapped('balance'))

    def test_company_setup(self):
        company = self.company
        self.assertEqual(company.chart_template, 'pf')
        self.assertEqual(company.account_fiscal_country_id, self.env.ref('base.pf'))
        self.assertEqual(company.income_account_id.code, '70710000')
        self.assertEqual(company.expense_account_id.code, '60710000')
        self.assertEqual(company.account_sale_tax_id, self._tax('tva_normale'))
        self.assertEqual(company.account_purchase_tax_id, self._tax('tva_acq_normale'))
        sale_journal = self.company_data['default_journal_sale']
        self.assertEqual(sale_journal.default_account_id.code, '70710000')
        bank_fees = self.env['account.chart.template'].with_company(company).ref(
            'bank_fees_reco', raise_if_not_found=False)
        if bank_fees:
            self.assertEqual(bank_fees.line_ids.account_id.code, '62780000')

    def test_account_codes_have_8_digits(self):
        # Accounts created from the template (not the extra ones the test
        # framework adds): their xmlid is account.<company id>_<template id>.
        data = self.env['ir.model.data'].search([
            ('model', '=', 'account.account'),
            ('module', '=', 'account'),
            ('name', '=like', f'{self.company.id}\\_%'),
            # created by Odoo when needed, as for the French chart
            ('name', '!=', f'{self.company.id}_unaffected_earnings_account'),
        ])
        codes = self.env['account.account'].browse(data.mapped('res_id')).with_company(self.company).mapped('code')
        self.assertTrue(codes)
        self.assertFalse([c for c in codes if len(c) != 8], "Account codes have 8 digits")

    def test_reduced_rate_taxes(self):
        sale = self._tax('tva_reduite')
        self.assertEqual(sale.price_include_override, False)
        self.assertFalse(sale.price_include, "tva_reduite is tax excluded")
        self.assertTrue(self._tax('tva_reduite_ttc').price_include)
        self.assertEqual(self._tax('tva_acq_reduite_ttc').invoice_label, 'TVA 5% TTC')
        invoice = self.init_invoice(
            'out_invoice', partner=self.partner, amounts=[1000.0], taxes=sale, post=True)
        self.assertAlmostEqual(invoice.amount_untaxed, 1000.0)
        self.assertAlmostEqual(invoice.amount_tax, 50.0)
        self.assertAlmostEqual(self._box(invoice, 'B05_taxe', -1), 50.0)

    def test_tax_tags_exist_and_unsigned(self):
        report = self.env.ref('l10n_pf.tax_report')
        formulas = report.line_ids.expression_ids.filtered(
            lambda e: e.engine == 'tax_tags').mapped('formula')
        expected = {f.lstrip('-') for f in formulas}
        taxes = self.env['account.tax'].search([('company_id', '=', self.company.id)])
        used = set(taxes.repartition_line_ids.tag_ids.mapped('name'))
        self.assertTrue(used, "The taxes carry no tag")
        self.assertFalse(
            {t for t in used if t[:1] in '+-'},
            "Tax tags are unsigned since 18.5")
        self.assertLessEqual(used, expected, "A tax feeds a tag absent from the report")

    def test_sale_tax_report_signs(self):
        tax = self._tax('tva_normale')
        invoice = self.init_invoice(
            'out_invoice', partner=self.partner, amounts=[1000.0], taxes=tax, post=True)
        refund = self.init_invoice(
            'out_refund', partner=self.partner, amounts=[400.0], taxes=tax, post=True)
        self.assertAlmostEqual(self._box(invoice, 'A01', -1), 1000.0)
        self.assertAlmostEqual(self._box(invoice, 'B07_base', -1), 1000.0)
        self.assertAlmostEqual(self._box(invoice, 'B07_taxe', -1), 160.0)
        moves = invoice | refund
        self.assertAlmostEqual(self._box(moves, 'A01', -1), 600.0)
        self.assertAlmostEqual(self._box(moves, 'B07_taxe', -1), 96.0)

    def test_purchase_tax_report_signs(self):
        tax = self._tax('tva_acq_normale')
        bill = self.init_invoice(
            'in_invoice', partner=self.partner, amounts=[1000.0], taxes=tax, post=True)
        refund = self.init_invoice(
            'in_refund', partner=self.partner, amounts=[250.0], taxes=tax, post=True)
        self.assertAlmostEqual(self._box(bill, 'C11'), 160.0)
        self.assertAlmostEqual(self._box(bill | refund, 'C11'), 120.0)

    def test_export_fiscal_position(self):
        detaxe = self.env['account.chart.template'].with_company(self.company).ref(
            'fiscal_position_template_detaxe')
        for xmlid in ('tva_normale', 'tva_normale_ttc', 'tva_intermediaire',
                      'tva_intermediaire_ttc', 'tva_reduite', 'tva_reduite_ttc'):
            self.assertEqual(detaxe.map_tax(self._tax(xmlid)), self._tax('tva_export'), xmlid)
        invoice = self.init_invoice(
            'out_invoice', partner=self.partner, amounts=[1000.0],
            taxes=self._tax('tva_export'), post=True)
        self.assertAlmostEqual(self._box(invoice, 'A03', -1), 1000.0)
