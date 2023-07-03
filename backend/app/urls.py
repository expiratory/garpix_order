from garpixcms.urls import *  # noqa

urlpatterns = [
    path('', include('garpix_order.urls')),
] + urlpatterns  # noqa
