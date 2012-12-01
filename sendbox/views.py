import requests                         # HTTP lib for python
import json                             # Python Standard Library - JSON utility
import elementtree.ElementTree as ET    # fast XML parser

from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext


def sendbox_index_view(request):
    '''
    Application Entry Point. Retrieves generated Box.com ticket upon construction.
    Facilitates app authentication with user's Box account
    '''
    url = u'https://www.box.com/api/1.0/rest'           # build url for ticket retrieval
    params = {'action': 'get_ticket',                   # build GET parameters
                'api_key': settings.BOX_API_KEY}
    context = {}
    try:
        response = requests.get(url, params=params)                 # GET request for ticket
        obj = ET.XML(response.content)                              # parse xml response to python object
        ticket = obj.findtext('ticket')                             # extract value from 'ticket' tag
        url = u'https://www.box.com/api/1.0/auth/%s' % ticket       # build url for Box.com ticket authentication
        context = {'ticket': ticket, 'url': url, }                  # template context (see django templates)
    except AttributeError:                                          # triggers when obj.find('ticket') asserts to None
        messages.error(request, "Invalid API Key!")                 # django message dispatcher (see django messages doc)
        pass

    if request.session.get('auth_token'):                           # check if auth_token exists
        context['auth_token'] = request.session.get('auth_token')   # add it to context for displaying to user

    return render_to_response('sendbox/index.html',                 # HttpResponse shortcut (see django shortcuts doc)
                                context,
                                    context_instance=RequestContext(request))


def get_auth_token_handler(request):
    '''
    Receives: POST data 'ticket' OR GET request with parameters 'auth_token' and 'ticket' from Box.com
    Pairs authenticated ticket with Box API Key to retreive Auth auth_token
    needed for accessing user Box files and folders.
    '''

    if request.session.get('auth_token'):                           # if an active session is present
        return redirect('sendbox_app_view', folder_id=0)            # redirect to main app page

    if request.method == 'POST' and request.POST.get('ticket'):  # if POST request was made
            url = u'https://www.box.com/api/1.0/rest'            # build request url for auth_token retrieval
            params = {'action': 'get_auth_token',                # build GET parameters
                        'api_key': settings.BOX_API_KEY,
                            'ticket': request.POST['ticket']}
            try:
                response = requests.get(url, params=params)         # GET request for auth_token retrieval
                obj = ET.XML(response.content)                      # parse xml response to python object
                auth_token = obj.findtext('auth_token')             # extract value from 'auth_token' tag
                request.session['auth_token'] = auth_token          # store auth_token in session key (see django sessions doc)
                return redirect('sendbox_app_view', folder_id=0)    # redirect to main app page
            except AttributeError:
                messages.error(request, "Invalid Ticket! Try logging in again!")
                return redirect('sendbox_index_view')                    # django reverse() shortcut (see django shortcuts doc)

    if request.GET.get('auth_token') and request.GET.get('ticket'):     # if GET parameters are present (for Box.com redirection)
        request.session['auth_token'] = request.GET['auth_token']   # just store auth_token in session key
        return redirect('sendbox_app_view', folder_id=0)            # redirect to main app page

    messages.error(request, "Cannot access this page directly!")
    return redirect('sendbox_index_view')                           # redirect to home page


def sendbox_app_view(request, folder_id=0):     # if folder_id = 0: get all items from root directory else: get items from 'folder_id'
    '''
    Main Application View. Displays table of all files and folders on current 'folder_id'.
    Allows simple folder navigation and provides 'share links' for files.
    '''
    if request.session.get('auth_token'):
        url = "https://api.box.com/2.0/folders/%s" % folder_id                      # build request url for folder operations
        headers = {'Authorization': 'BoxAuth api_key=%s&auth_token=%s' %            # build request headers for authentication
                (settings.BOX_API_KEY, request.session.get('auth_token'))}
        context = {}
        try:
            response = requests.get(url, headers=headers)                           # GET request for items inside 'folder_id'
            obj = json.loads(response.content)                                      # deserialize json response to python dictionary
            user_email = obj['owned_by']['login']                                   # gets user email for use as sender email
            folder = obj['name']                                                    # returns current folder name
            items = obj['item_collection']['entries']                               # returns list of files and folders on current folder
            parent = obj['parent']                                                  # returns parent folder, if any
            context = {'items': items, 'parent': parent,                            # build template context
                    'folder': folder, 'subject': settings.DEFAULT_SUBJECT}
            request.session['user_email'] = user_email                              # store user_email in session key for use later
        except KeyError:
            messages.error(request, "Error Code: %s" % obj['code'] or "unknown")    # returns error code from box api response
            pass

        return render_to_response('sendbox/sendbox.html',                           # go to main app page whatever the case
            context, context_instance=RequestContext(request))                      # - if session is still active

    messages.error(request, "You have to login!")
    return redirect('sendbox_index_view')                        # redirect to home page if session is empty


def sendbox_processor(request):
    '''
    Receives: POST value 'file_id', 'email', 'subject', 'message'
    Generates Share Link based on file_id
    '''
    if request.method == 'POST' and request.POST.get('file_id') and request.POST.get('email'):
        url = "https://api.box.com/2.0/files/%s" % request.POST['file_id']          # build request url for file operations
        headers = {'Authorization': 'BoxAuth api_key=%s&auth_token=%s' %            # build request headers for authentication
                (settings.BOX_API_KEY, request.session.get('auth_token'))}
        data = json.dumps({'shared_link': {'access': 'Open'}})                      # serialize http data to JSON for PUT request
        try:
            response = requests.put(url, headers=headers, data=data)                # PUT request for shared link generation
            obj = json.loads(response.content)                                      # deserialize JSON response
            filename = obj['name']                                                  # returns file name
            shared_link = obj['shared_link']['url']                                 # returns file url
            folder_id = obj['parent']['id']                                         # returns folder_id of file parent
            messages.success(request, 'Shared Link for file "%s" is: "%s"' %        # by this time, shared link is already generated
                (filename, shared_link))

            sendgrid = sendgrid_email_handler(request, filename, shared_link)       # call utility function for sending our mail

            messages.info(request, 'SendGrid Response Code: %s' % sendgrid['message'])  # returns status code from sendgrid response
            return redirect('sendbox_app_view', folder_id=folder_id)                # redirect to main app

        except KeyError:
            messages.error(request, "Error Code: %s" % obj['code'] or "unknown")    # returns error code from box api response
            pass

    return redirect('sendbox_app_view', folder_id=0)    # redirect to main app when accessed directly


def logout(request):
    request.session.flush()                 # clear server-side session vars
    messages.error(request, "Logged Out!")
    return redirect('sendbox_index_view')   # redirect to index page


def sendgrid_email_handler(request_vars, filename, shared_link):
    '''
    Utility function. Sends message to chosen email recipients.
    Returns json response from SendGrid
    '''
    # Email Section
    subject = request_vars.POST['subject'] or settings.DEFAULT_SUBJECT         # use default subject if none is provided
    message = '%s\n\n\nFile Name: "%s"\n\nBox Shared Link: "%s"' % (           # build message body
                request_vars.POST['message'], filename, shared_link)           # - append box file info and link at the end of message

    emails = request_vars.POST['email'].replace(" ", "").split(',')      # remove whitespace from 'email' POST var and split on ','
                                                                               # - must be a python list object even if single
    from_email = request_vars.session['user_email']                            # grab user email from session variable

    params = {'api_user': settings.SENDGRID_API_USER,                  # build GET parameters
                'api_key': settings.SENDGRID_API_KEY,
                  'to': emails[:5],                              # limits to first 5 emails for the sake of my SendGrid server :)
                    'subject': subject,
                      'text': message,
                        'from': from_email, }
    sendgrid_request = requests.get(settings.SENDGRID_API_URL, params=params)   # GET request for sending email to SendGrid API
    sendgrid_response = json.loads(sendgrid_request.content)

    return sendgrid_response                                    # returns response from SendGrid API
