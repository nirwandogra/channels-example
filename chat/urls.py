from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$',  views.about, name='about'),
    url(r'^new/$', views.new_room, name='new_room'),
    url(r'^(?P<label>[\w-]{,50})/$', views.chat_room, name='chat_room'),
    url(r'^record/uploadAudioFile/$', views.uploadAudioFile,
        name='uploadAudioFile'),

    url(r'^call/(?P<callId>[\w-]{,200})$', views.getCallById,
        name='getCallById'),

    url(r'^callPunchuatedText/(?P<callId>[\w-]{,200})$', views.callPunchuatedText,
        name='callPunchuatedText'),
]