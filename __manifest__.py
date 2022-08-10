# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'French Polynesia - Accounting',
    'version': '0.1',
    'category': 'Localization',
    'description': """
This is the module to manage the accounting chart for French Polynesia in Odoo.
========================================================================

**Credits:** France accounting chart.
""",
    'depends': ['account'],
    'data': [
        'data/l10n_pf_chart_data.xml',
        'data/account_chart_template_data.xml',
        'views/l10n_pf_view.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_data.xml'
    ],
}
