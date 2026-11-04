# l10n_pf — French Polynesia accounting (Odoo 19.0)

Chart of accounts, taxes, fiscal positions and VAT return for companies
based in French Polynesia.

## Branches

One branch per Odoo version (`17`, `18`, `19`). Never merge a version branch
into another one.

## Upgrade from 17.0

- `migrations/19.0.1.1.0/pre-migrate.py`: copies the former TAHITI fields into
  the tax identifier (`vat`) when it is empty, logs the conflicts. Skipped on
  databases that already ran this merge in 17.0 (l10n_pf 17.0.0.3.0).
- `migrations/19.0.1.1.0/end-migrate_update_taxes.py`: reloads the chart on
  every company using it (`try_loading(..., force_create=False)`), so that the
  unsigned tax tags and the fiscal position links of 19.0 reach the existing
  taxes. It also fixes the invoice label of "ACH-5% TTC".
- The "5%" sale tax (`tva_reduite`) is tax excluded since 19.0.1.1.0 on new
  companies. Existing companies keep their setting: switching it would make
  the prices of the products sold with this tax be read as tax excluded.
  Check its use and change it by hand if needed.
- Account codes have 8 digits (`code_digits`), as on the 17.0 databases.

After the upgrade, compare a VAT return before and after on a copy of the
production database.

## Tests

```bash
odoo-bin -d test19 -i l10n_pf --test-enable --test-tags /l10n_pf --stop-after-init
```
