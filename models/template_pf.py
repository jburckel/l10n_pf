# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('pf')
    def _get_pf_template_data(self):
        return {
            'code_digits': 8,
            'property_account_receivable_id': 'pf_pcg_recv',
            'property_account_payable_id': 'pf_pcg_pay',
        }

    @template('pf', 'res.company')
    def _get_pf_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.pf',
                'bank_account_code_prefix': '512',
                'cash_account_code_prefix': '53',
                'transfer_account_code_prefix': '58',
                'account_default_pos_receivable_account_id': 'pf_pcg_recv_pos',
                'income_currency_exchange_account_id': 'pcg_766',
                'expense_currency_exchange_account_id': 'pcg_666',
                'account_journal_early_pay_discount_loss_account_id': 'pcg_665',
                'account_journal_early_pay_discount_gain_account_id': 'pcg_765',
                'l10n_pf_rounding_difference_loss_account_id': 'pcg_658',
                'l10n_pf_rounding_difference_profit_account_id': 'pcg_758',
                'account_sale_tax_id': 'tva_normale',
                'account_purchase_tax_id': 'tva_acq_normale',
                'income_account_id': 'pcg_7071',
                'expense_account_id': 'pcg_6071',
            },
        }

    @template('pf', 'account.journal')
    def _get_pf_account_journal(self):
        return {
            'sale': {'refund_sequence': True},
            'purchase': {'refund_sequence': True},
        }

    def _get_bank_fees_reco_account(self, company):
        # Polynesian account for the standard "Bank fees" reconciliation
        # model (627800, padded to 8 digits on new companies). Be as precise as possible: if the account was modified, fall
        # back on the standard choice instead of picking a wrong one.
        pf_account = self.env['account.account'].with_company(company).search([
            *self.env['account.account']._check_company_domain(company.id),
            ('code', 'in', ('627800', '62780000')),
            ('account_type', '=', 'expense'),
            ('name', '=', 'Other expenses and commissions on services supplied'),
        ], limit=1)
        return pf_account or super()._get_bank_fees_reco_account(company)
