from garpixcms.settings import *  # noqa

INSTALLED_APPS += [
    'garpix_order',
    'example',
    'fsm_admin'
]

MIGRATION_MODULES.update({  # noqa:F405
    'fcm_django': 'app.migrations.fcm_django',
    'garpix_order': 'app.migrations.garpix_order'
})
