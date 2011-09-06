import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404

from storm.locals import *

import forms
from barabasdjango.webserver import WebServer
from barabasdjango.users.decorators import LoginRequired
from barabas.objects.syncedfile import SyncedFile, FileTag
from barabas.objects.syncedfileversion import SyncedFileVersion

class UploadedFileWrapper:
    def __init__(self, upload):
        """Empty docstring"""
        self.__upload = upload
        self.__temp = open(self.__upload.temporary_file_path())
    
    def seek(self, offset):
    	return self.__temp.seek(offset)
    
    def tell(self):
    	return self.__temp.tell()
    
    def read(self, length = None):
        """Empty docstring"""
        return self.__temp.read(length)

def index(request):
    if request.user:
        db = WebServer().database()
        tags = db.find(FileTag.tagName, SyncedFile.ID == FileTag.fileID,
                                SyncedFile.owner == request.user) \
                 .group_by(FileTag.tagName) \
                 .order_by(Desc(Count(SyncedFile.ID)))
        
        createFileForm = forms.CreateFileForm()
        return render_to_response('barabas/index.html',
                                  {
                                   'tagCloud': tags,
                                   'createFileForm': createFileForm
                                  },
                                  context_instance=RequestContext(request))
    else:    
        return render_to_response('barabas/index_anon.html',
                                  context_instance=RequestContext(request))

@LoginRequired
def viewFiles(request, tagName):
    database = WebServer().database()
    fileList = SyncedFile.findWithTags(database, request.user, (tagName, ))

    return render_to_response('barabas/fileList.html', { 'files' : fileList },
                              context_instance=RequestContext(request))

@LoginRequired
def viewFile(request, fileID):
    syncedFile = WebServer().database().find(SyncedFile, SyncedFile.ID == int(fileID)).one()

    if syncedFile == None:
        raise Http404

    if (syncedFile.owner != request.user):
        return HttpResponseRedirect('/')
    
    uploadVersionForm = forms.UploadNewVersionForm()
    tagFileForm = forms.TagFileForm()
    return render_to_response('barabas/file.html', { 'versions': syncedFile.versions,
                                                 'uploadVersionForm': uploadVersionForm,
                                                 'tagFileForm': tagFileForm,
                                                 'file': syncedFile },
                              context_instance=RequestContext(request))

@LoginRequired
def tag(request, fileID):
    if request.method == "POST":
        tagForm = forms.TagFileForm(request.POST)
        
        if (tagForm.is_valid()):
            database = WebServer.database()
            
            syncedFile = database.find(SyncedFile, SyncedFile.ID == int(fileID)).one()
            if (syncedFile.owner != request.user):
                return HttpResponseRedirect('/')
            
            syncedFile.tag(tagForm.cleaned_data['tagName'])
            database.commit()
            return HttpResponseRedirect('/files/' + str(syncedFile.ID) + '/')

@LoginRequired
def uploadVersion(request, fileID):
    if request.method == "POST":
        uploadVersionForm = forms.UploadNewVersionForm(request.POST, request.FILES)
        
        if (uploadVersionForm.is_valid()):
            storage = WebServer.storage()
            database = WebServer.database()
            
            syncedFile = database.find(SyncedFile, SyncedFile.ID == int(fileID)).one()
        
            if (syncedFile.owner != request.user):
                return HttpResponseRedirect('/')
            
            uploadedFile = uploadVersionForm.cleaned_data['syncedFile']
            version = SyncedFileVersion(UploadedFileWrapper(uploadedFile),
                                        u'Version from %s (from web)' % datetime.datetime.now(WebServer.timezone()).strftime('%Y-%m-%d %H:%M'),
                                        unicode(datetime.datetime.now(WebServer.timezone()).strftime('%Y-%m-%dT%H:%M:%S%z')),
                                        storage)
            syncedFile.add_version(version)
            database.commit()
            return HttpResponseRedirect('/files/' + str(syncedFile.ID) + '/')

@LoginRequired
def createFile(request):    
    if (request.method == "POST"):
        createFileForm = forms.CreateFileForm(request.POST, request.FILES)
        if (createFileForm.is_valid()):
            storage = WebServer.storage()
            database = WebServer.database()
                        
            uploadedFile = createFileForm.cleaned_data['syncedFile']
            sf = SyncedFile(uploadedFile.name, request.user)
            sf.mimetype = unicode(uploadedFile.content_type)
            sf.add_to_store(database)
            
            version = SyncedFileVersion(UploadedFileWrapper(uploadedFile),
                                        u'Initial Version (from web)',
                                        unicode(datetime.datetime.now(WebServer.timezone()).strftime('%Y-%m-%dT%H:%M:%S%z')),
                                        storage)
            sf.add_version(version)
            database.commit()
            
            return HttpResponseRedirect('/files/' + str(sf.ID) + '/')
        else:
            return render_to_response('barabas/createFile.html', { 'createFileForm': createFileForm },
                                      context_instance=RequestContext(request))

@LoginRequired
def download(request, fileID, versionID):
    storage = WebServer.storage()
    database = WebServer.database()
    
    version = database.find(SyncedFileVersion, SyncedFileVersion.ID == int(versionID)).one()
    if (version.syncedfile.owner != request.user):
        return HttpResponseRedirect('/')
    filed = version.open(storage)
    
    resp = HttpResponse(filed, mimetype=version.syncedfile.mimetype)
    resp['Content-Disposition'] = 'attachment; filename='+version.syncedfile.fileName
    return resp
