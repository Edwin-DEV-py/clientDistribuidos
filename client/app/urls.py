from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('loguin/', LoguinView.as_view(), name='loguin'),
    path('carpetas/', FolderView.as_view(), name='carpetas'),
    re_path(r'^carpetas/(?P<folderId>\d+)/$', FolderView.as_view(), name='carpetasPadre'),
    path('archivos/', FileView.as_view(), name='archivos'),
    re_path(r'^archivos2/(?P<fileId>\d+)/$', FileView2.as_view(), name='archivos2id'),
    path('archivos2/', FileView2.as_view(), name='archivos2'),
    path('carpetas2/', folder2View.as_view(), name='carpetas2'),
]
