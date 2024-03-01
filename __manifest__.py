# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'French Polynesia - Accounting',
    'website': 'https://github.com/jburckel/l10n_pf',
    'icon': '/account/static/description/l10n.png',
    'countries': ['pf'],
    'version': '0.1',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This is the module to manage the accounting chart for French Polynesia in Odoo.
========================================================================

This module applies to companies based in French Polynesia mainland. 

**Credits:** Sistheo, Zeekom, CrysaLEAD, Akretion, Camptocamp and Natimai Solutions.
""",
    'depends': [
        'base_iban',
        'base_vat',
        'account',
    ],
    'data': [
        'data/account_chart_template_data.xml',
        'data/account_data.xml',
        'views/l10n_pf_view.xml',
        'data/tax_report_data.xml',
        'data/res_country_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'post_init_hook': '_l10n_pf_post_init_hook',
    'license': 'LGPL-3',
}
