from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import JsonResponse
import jwt
from zeep import Client
import base64
from .serializers import *
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime
import os
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser


clientUser = Client('http://172.171.240.20:80/users/soap/?wsdl')
clientFolder = Client('http://172.171.240.20:80/server/soap/?wsdl')
clientFile= Client('http://172.171.240.20:80/files/soap/?wsdl')

#region metodos de usuarios
class LoguinView(APIView):
    
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username', None)
        password = data.get('password', None)
        serializers = UserCredentialsSerializer(data={'username': username, 'password': password})
        
        if serializers.is_valid():
            username = serializers.validated_data.get('username')
            password = serializers.validated_data.get('password')
            response = clientUser.service.loginSoap(username,password)


            return Response({'token':response})
    
def registerView (username, email, name, age, password):
    
    serializers = UserDataSerializer(data={'username': username, 'password': password})
    
    if serializers.is_valid():
        
        username = serializers.validated_data.get('username')
        name = serializers.validated_data.get('name')
        email = serializers.validated_data.get('email')
        age = serializers.validated_data.get('age')
        password = serializers.validated_data.get('password')
        
        response = clientUser.service.resgisterSoap(username, name, email, age, password)
        
        return response
            
#endregion

#region metodos carpeta

class FolderView(APIView):
    
    def get(self, request, folderId):
        
        token = request.headers.get('Authorization')
        
        folders = clientFolder.service.get_folders_by_parent_id(token,folderId)
        
        data = []
        
        if folders != None:
            for item in folders:
                if item['type'] == 'folder':
                    storage_value = 0 if item['storage'] is None else item['storage']
                    
                    folder_data = {
                        'id': item['id'],
                        'folderName': item['folderName'],
                        'parentFolder': item['parentFolder'],
                        'userId': item['userId'],
                        'type': item['type'],
                        'storage': storage_value,
                    }
                    data.append(folder_data)
                elif item['type'] == 'file':
                    parent = 0 if item['parentFolder'] is None else item['parentFolder']
                    file_data = {
                        'id': item['id'],
                        'fileName': item['fileName'],
                        'parentFolder': parent,
                        'userId': item['userId'],
                        'type': item['type'],
                        'extension': item['extension'],
                    }
                    data.append(file_data)
        else:
            data = []
        return Response({'data': data,})
    
    def post(self, request):
        
        folderName = request.data.get('folderName')
        token = request.headers.get('Authorization')
        folderParent = request.data.get('folderParent')
        
        print(request.data)
        agregar = clientFolder.service.registerFolderSoap(token,folderName,folderParent)
        
        if agregar != None:
            return Response('exito')
        else:
            return Response('mal')
    
    def put(self, request):
        
        folderName = request.data.get('folderName')
        token = request.headers.get('Authorization')
        folderId = request.data.get('folderId')
        folderParent = request.data.get('folderParent')

        editar = clientFolder.service.updateFolderSoap(token, folderId, folderName, folderParent)
        
        if editar != None:
            return Response('exito')
        else:
            return Response('mal')
    
    def delete(self, request, folderId):
        
        token = request.headers.get('Authorization')

        eliminar = clientFolder.service.deleteFolderSoap(token, folderId)
        print(eliminar)
        return Response(eliminar)

class folder2View(APIView):
    
    def get(self, request):
        token = request.headers.get('Authorization')
        
        folders = clientFolder.service.get_all_folders(token)
        
        data = []
        
        if folders != None:
            for item in folders:
                if item['type'] == 'folder':
                    folder_data = {
                        'id': item['id'],
                        'folderName': item['folderName'],
                    }
                    data.append(folder_data)
                    
        else:
            data = []
            
        print(data)
        return Response({'data': data,})
    
def convert_to_serializable(self, obj):
        if isinstance(obj, dict):
            return {k: self.convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self.convert_to_serializable(i) for i in obj]
        elif hasattr(obj, '__dict__'):
            return self.convert_to_serializable(obj.__dict__)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return obj
#endregion

#region metodos archivo

def encode_image(uploaded_file):
    encoded_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
    return encoded_image

def get_filename(image_path):
    return os.path.basename(image_path)

def get_filesize(image_path):
    return os.path.getsize(image_path)

class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self,request,*args,**kwargs):
        token = request.headers.get('Authorization')
        folder_id = request.data.get('folder_id')
        files = request.FILES.getlist('files')
        print(files)
        files_info = []
        
        for image_path in files:
            filename = image_path.name
            filesize = image_path.size
            encoded_image = encode_image(image_path)
            file_sha256 = 'hola'
            files_info.append({"filename": filename, "filesize": filesize, "encoded_image": encoded_image, "file_hash": file_sha256})

        for file_info in files_info:
            response = clientFile.service.process_file(token, file_info["filename"], file_info["filesize"], file_info["encoded_image"], file_info["file_hash"], folder_id)

        return Response('yes')

    
class FileView2(APIView):
    
    def get(self, request, fileId):
        token = request.headers.get('Authorization')
        
        response = clientFile.service.download_file(token, fileId)
        
        return Response(response)
    
    def put(self, request):
        
        fileName = request.data.get('fileName')
        token = request.headers.get('Authorization')
        fileId = request.data.get('fileId')
        folderParent = request.data.get('folderParent')
        print(request)
        response = clientFile.service.update_file(token, fileId, fileName, folderParent)

        print(response)
        
        return Response('exito')
    
    def delete(self,request, fileId):
        
        token = request.headers.get('Authorization')
        
        response = clientFile.service.delete_file(token, fileId)
        
        return Response('exito')
#endregion


