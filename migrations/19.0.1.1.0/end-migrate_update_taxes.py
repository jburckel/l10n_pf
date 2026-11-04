# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Reload the Polynesian chart on the existing companies.

The chart template is only loaded at the first installation: on an upgrade,
the 19.0 tax tags, fiscal position links and company settings reach the
existing companies through this reload. ``force_create=False`` updates the
records created from the template without creating the missing ones, so the
script can be replayed. It runs at the ``end`` stage, once every module of
the database is loaded (at the ``post`` stage, the fields added to
``account.account`` by modules not yet upgraded, such as ``create_asset``,
are missing from the registry and the reload fails).

An existing tax keeps its own settings (the reload only rewrites its tags and
fiscal positions): the invoice label of "ACH-5% TTC" is fixed here. The
switch of "5%" (tva_reduite) from tax included to tax excluded is NOT applied
to existing companies: the products sold with this tax would see their price
interpreted as tax excluded. Check its use and change it by hand if needed.
"""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search(
        [('chart_template', '=', 'pf')], order='parent_path')
    for company in companies:
        env['account.chart.template'].try_loading('pf', company, force_create=False)
        tax = env['account.chart.template'].with_company(company).ref(
            'tva_acq_reduite_ttc', raise_if_not_found=False)
        if tax and tax.invoice_label == 'TVA 5%':
            tax.invoice_label = 'TVA 5% TTC'
