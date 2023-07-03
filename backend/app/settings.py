from garpixcms.settings import *  # noqa

INSTALLED_APPS += [
    'example',
    'fsm_admin',
    'garpix_order',
]

MIGRATION_MODULES.update({  # noqa:F405
    'fcm_django': 'app.migrations.fcm_django',
    'garpix_order': 'app.migrations.garpix_order'
})
