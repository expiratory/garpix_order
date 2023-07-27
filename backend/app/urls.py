from garpixcms.urls import *  # noqa

urlpatterns = [
    path('', include(('garpix_order.urls', 'order'), namespace='garpix_order')),
] + urlpatterns  # noqa
