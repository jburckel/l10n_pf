# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Merge the TAHITI numbers into the tax identifier.

The TAHITI number used to be a separate stored field on partners and
companies; it now derives from the standard ``vat`` field. Before the new
definitions are loaded, every TAHITI number is copied into the tax identifier
of its partner (or of the company's partner) when that identifier is empty. A
record holding both, with different values, is left untouched and reported in
the log for a manual check.

Databases that already ran this merge in 17.0 (l10n_pf 17.0.0.3.0) are
skipped: their old ``tahiti`` columns are stale, and copying them again would
bring back numbers removed since.
"""
import logging
import re

from odoo.tools import parse_version
from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def _normalize(value):
    number = re.sub(r'[\s.\-]', '', value or '').upper()
    if number.startswith('PF') and len(number) > 2:
        number = number[2:]
    return number


def _merge(cr, query, label, conflicts):
    cr.execute(query)
    for record_id, name, tahiti, partner_id, vat in cr.fetchall():
        if not (vat or '').strip():
            cr.execute("UPDATE res_partner SET vat = %s WHERE id = %s",
                       (tahiti.strip(), partner_id))
        elif _normalize(vat) != _normalize(tahiti):
            conflicts.append("%s %s (id %s): VAT %r, TAHITI %r"
                             % (label, name, record_id, vat, tahiti))


def migrate(cr, version):
    if not version or parse_version(version) >= parse_version('17.0.0.3.0'):
        return

    conflicts = []
    if column_exists(cr, 'res_partner', 'tahiti'):
        _merge(cr, """
            SELECT id, name, tahiti, id, vat FROM res_partner
             WHERE tahiti IS NOT NULL AND btrim(tahiti) <> ''
        """, 'partner', conflicts)
    if column_exists(cr, 'res_company', 'tahiti'):
        _merge(cr, """
            SELECT c.id, c.name, c.tahiti, p.id, p.vat
              FROM res_company c
              JOIN res_partner p ON p.id = c.partner_id
             WHERE c.tahiti IS NOT NULL AND btrim(c.tahiti) <> ''
        """, 'company', conflicts)

    if conflicts:
        _logger.warning(
            "l10n_pf: %s record(s) hold a TAHITI number different from their "
            "tax identifier; the tax identifier was kept, check them "
            "manually:\n%s", len(conflicts), "\n".join(conflicts))
