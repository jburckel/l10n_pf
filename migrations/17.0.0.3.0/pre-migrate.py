# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Merge the TAHITI numbers into the tax identifier.

The TAHITI number used to be a separate stored field on partners and
companies; it now derives from the standard ``vat`` field. Before the new
definitions are loaded, every TAHITI number is copied into the tax
identifier of its partner (or of the company's partner) when that identifier
is empty. A partner holding both, with different values, is left untouched
and reported in the log for a manual check.
"""
import logging
import re

_logger = logging.getLogger(__name__)


def _normalize(value):
    number = re.sub(r'[\s.\-]', '', value or '').upper()
    if number.startswith('PF') and len(number) > 2:
        number = number[2:]
    return number


def _column_exists(cr, table, column):
    cr.execute("""
        SELECT 1 FROM information_schema.columns
         WHERE table_name = %s AND column_name = %s
    """, (table, column))
    return bool(cr.fetchone())


def migrate(cr, version):
    conflicts = []

    if _column_exists(cr, 'res_partner', 'tahiti'):
        cr.execute("""
            SELECT id, name, vat, tahiti FROM res_partner
             WHERE tahiti IS NOT NULL AND btrim(tahiti) <> ''
        """)
        for partner_id, name, vat, tahiti in cr.fetchall():
            if not (vat or '').strip():
                cr.execute("UPDATE res_partner SET vat = %s WHERE id = %s",
                           (tahiti.strip(), partner_id))
            elif _normalize(vat) != _normalize(tahiti):
                conflicts.append("partner %s (id %s): VAT %r, TAHITI %r"
                                 % (name, partner_id, vat, tahiti))

    if _column_exists(cr, 'res_company', 'tahiti'):
        cr.execute("""
            SELECT c.id, c.name, c.tahiti, p.id, p.vat
              FROM res_company c
              JOIN res_partner p ON p.id = c.partner_id
             WHERE c.tahiti IS NOT NULL AND btrim(c.tahiti) <> ''
        """)
        for company_id, name, tahiti, partner_id, vat in cr.fetchall():
            if not (vat or '').strip():
                cr.execute("UPDATE res_partner SET vat = %s WHERE id = %s",
                           (tahiti.strip(), partner_id))
            elif _normalize(vat) != _normalize(tahiti):
                conflicts.append("company %s (id %s): VAT %r, TAHITI %r"
                                 % (name, company_id, vat, tahiti))

    if conflicts:
        _logger.warning(
            "l10n_pf: %s record(s) hold a TAHITI number different from "
            "their tax identifier; the tax identifier was kept, check them "
            "manually:\n%s", len(conflicts), "\n".join(conflicts))
