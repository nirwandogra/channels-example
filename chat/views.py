from rake_nltk import Rake
import re
import RAKE
import requests
import traceback
import uuid
import os
import re
import json
import urlparse
from models import *
from django.views.generic import View
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
import random
import string
from django.db import transaction
from django.shortcuts import render, redirect
import haikunator
from .models import Room
import urllib2
import speech_recognition as sr
import subprocess
import os
import urllib
import hashlib
import os
import json
import datetime
import requests

def about(request):
    return render(request, "chat/about.html")

def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    while not new_room:
        with transaction.atomic():
            label = haikunator.haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room = Room.objects.create(label=label)
    return redirect(chat_room, label=label)

def chat_room(request, label):
    """
    Room view - show the room, with latest messages.

    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chat/room.html", {
        'room': room,
        'messages': messages,
    })

def convert_date(s):
    try: 
        return int(datetime.datetime.strptime(s, '%Y-%m-%d').strftime("%s"))*1000
    except ValueError:
        return False

def convert_int(s):
    try:
        return int(s)
    except ValueError:
        return None

def convert_bool(s):
    try:
        s = s.lower()
        if s == 'true' or s == 'on':
            return True
        elif s == 'false' or s == 'off':
            return False
    except ValueError:
        return None

def convert_value(attribute, value):
    try:
        value = str(value)
        value_int = convert_int(value)
        value_bool = convert_bool(value)
        value_date = convert_date(value)
        if value_int or value_int == 0:
            value = value_int
        if value_bool is not None:
            value = value_bool
        if value_date:
            value = value_date
        return value
    except Exception as e:
        return value

def clean_data(data):
    try:
        data = dict(data.iterlists())
        data = get_single(data)
        for d in data:
            if type(data[d]) == list:
                for i,a in enumerate(data[d]):
                    data[d][i] = convert_value(d, data[d][i])
            else:
                data[d] = convert_value(d, data[d])
        return data
    except Exception as e:
        return data

def get_single(keys):
    res = {}
    for key in keys:
        if len(keys[key]) == 1:
            if ',' in keys[key][0]:
                res[key] = keys[key][0].split(',')
            else:
                res[key] = keys[key][0]
        else:
            res[key] = keys[key]
    return res

def uploadAudioFile(request, *args, **kwargs):
    print 'testing';
    options = {
        'error': 'only post request configured over this endpoint'
    }
    print request.POST;
    if not request.POST:
        return HttpResponse(json.dumps(options),content_type='application/json');
    deal = {
        'testing':'hello world'
    }
    print request.POST
    attributes = clean_data(request.POST)
    print attributes
    save_and_upload(request, attributes)
    options = get_single(
                json.loads(json.dumps(urlparse.parse_qs(request.META['QUERY_STRING']))))

    return HttpResponse(json.dumps(options),content_type='application/json');

def save_and_upload(request, attributes):
    try:
        for f in request.FILES:
            unique_id = uuid.uuid4()
            data = request.FILES[f]
            loc = 'tmp/'+ str(unique_id) + '.wav'
            path = default_storage.save(
                loc, ContentFile(data.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            print tmp_file
            print 'Converting Text to speech '
            r = sr.Recognizer()
            with sr.AudioFile(tmp_file) as source:
                r.adjust_for_ambient_noise(source)
                audio = r.record(source)
            command = r.recognize_google(audio)
            print command
            options = {}
            options['path'] = tmp_file
            options['text'] = command
            if 'callId' in attributes:
                options['callId'] = attributes['callId']
            saveNewCallIntoDB(options);
    except Exception as e:
        traceback.print_exc()

def createCall():
    unique_id = uuid.uuid4()
    print str(unique_id)
    call = Call(call_id=str(unique_id))
    call.save()
    return call

def createFile(call, path, text):
    filee = File(name=path,text=text,callId=call)
    filee.save()
    return filee

def saveNewCallIntoDB(options):
    print options
    if 'callId' not in options:
        call = createCall()
        return createFile(call, options['path'], options['text'])
    else:
        callId = options['callId']
        call = Call.objects.get(call_id=callId)
        return createFile(call, options['path'], options['text'])


def get_objects(objs, flag=0):
    if flag == 0:
        return [obj.get_json() for obj in objs ]
    else:
        return [obj.get_json(flag=flag) for obj in objs]

def getCallById(request, callId):
    options = {
        'callId':callId
    }
    call = Call.objects.filter(call_id=callId);
    print '###' , call;
    fileData = {}
    if(len(call) > 0):
        id = call[0].id
        print id
        fileData = get_objects(File.objects.filter(callId_id=id));
        print fileData
    return HttpResponse(json.dumps(fileData),content_type='application/json');

def callPunchuatedText(request, callId):
    options = {
        'callId':callId
    }
    call = Call.objects.filter(call_id=callId);
    print '###' , call;
    fileData = {}
    if(len(call) > 0):
        id = call[0].id
        print id
        fileData = get_objects(File.objects.filter(callId_id=id));
        text = ''
        for f in fileData:
            text = f['text'] + text + ' ';
        print 'Getting punchuated text :'
        r = requests.post("http://bark.phon.ioc.ee/punctuator", 
            data={'text': text});
        print 'Received punchuated text from punctuator service .'
        text = r.content;
        
        xx = RAKE.Rake(RAKE.SmartStopList())
        keywords = xx.run(text,minCharacters = 1, maxWords = 1, minFrequency = 1)[0:5]

        ra = Rake()
        ra.extract_keywords_from_text(text)
        phrases = ra.get_ranked_phrases()[0:5]

        for phrase in phrases:
            boldKeyword = '<b>' + phrases[0] + '</b>'
            insensitive_hippo = re.compile(re.escape([phrase][0]), re.IGNORECASE)
            text = insensitive_hippo.sub(boldKeyword,text)

        response = {
            'text':text,
            'keywords':keywords
        }
    return HttpResponse(json.dumps(response),content_type='application/json');

