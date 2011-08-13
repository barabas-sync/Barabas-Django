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
        self.__currentChunk = 0
        self.__chunks = self.__upload.chunks()
        self.__buffer = None
    
    def read(self, length = None):
        """Empty docstring"""
        if (length == None):
            return self.__upload.read()
        else:
            if (self.__buffer == None):
                self.__buffer = self.__upload.read()
            
            chunk = self.__buffer[:length]
            self.__buffer = self.__buffer[length:] 
            
            return chunk

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
            database = webserver.WebServer.database()
            
            syncedFile = database.find(SyncedFile, SyncedFile.ID == int(fileID)).one()
            if (syncedFile.owner != request.user):
                return HttpResponseRedirect('/')
            
            syncedFile.tag(tagForm.cleaned_data['tagName'])
            database.commit()
            return HttpResponseRedirect('/barabas/files/' + str(syncedFile.ID) + '/')

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
            version = storage.create(UploadedFileWrapper(uploadedFile), datetime.datetime.now())
            syncedFile.versions.add(version)
            database.commit()
            return HttpResponseRedirect('/barabas/files/' + str(syncedFile.ID) + '/')

@LoginRequired
def createFile(request):    
    if (request.method == "POST"):
        createFileForm = forms.CreateFileForm(request.POST, request.FILES)
        if (createFileForm.is_valid()):
            storage = WebServer.storage()
            database = WebServer.database()
                        
            uploadedFile = createFileForm.cleaned_data['syncedFile']
            sf = SyncedFile(uploadedFile.name, request.user)
            database.add(sf)
            
            version = SyncedFileVersion(UploadedFileWrapper(uploadedFile),
                                        u'Testname',
                                        datetime.datetime.now(),
                                        storage)
            sf.versions.add(version)
            database.flush()
            database.commit()
            
            return HttpResponseRedirect('/barabas/files/' + str(sf.ID) + '/')
        else:
            return render_to_response('barabas/createFile.html', { 'createFileForm': createFileForm },
                                      context_instance=RequestContext(request))

@LoginRequired
def download(request, fileID, versionID):
    storage = WebServer.storage()
    database = WebServer.database()
    
    version = database.find(FileVersion, FileVersion.ID == int(versionID)).one()
    if (version.syncedfile.owner != request.user):
        return HttpResponseRedirect('/')
    filed = version.open(storage)
    
    resp = HttpResponse(filed.read(), mimetype='application/octet-stream')
    filed.close()
    resp['Content-Disposition'] = 'attachment; filename='+version.syncedfile.fileName
    return resp
