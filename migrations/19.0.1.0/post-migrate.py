# Part of Odoo. See LICENSE file for full copyright and licensing details.
# try_loading is intentionally omitted here: calling it before the registry is
# fully loaded (post-migrate stage) triggers a NOT NULL violation on
# account_account.create_asset in v19. The chart template is refreshed
# automatically by the standard module-upgrade mechanism instead.
def migrate(cr, version):
    pass
