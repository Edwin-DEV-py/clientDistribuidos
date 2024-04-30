from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import jwt
from zeep import Client
import base64

from client.app.serializers import *

clientUser = Client('http://207.248.81.74:80/users/soap/?wsdl')
clientFolder = Client('http://207.248.81.74:80/server/soap/?wsdl')
clientFile= Client('http://207.248.81.74:80/files/soap/?wsdl')

#region metodos de usuarios

def loginView (username, password):
    
    serializers = UserCredentialsSerializer(data={'username': username, 'password': password})
    
    if serializers.is_valid():
        
        username = serializers.validated_data.get('username')
        password = serializers.validated_data.get('password')
        
        response = clientUser.service.loginSoap(username,password)
        
        return response
    
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
    
    def get(self, request):
        
        token = request.data.get('token')
        
        folders = clientFolder.service.get_folders_by_parent_id(token,0)
        
        return Response(folders)
    
    def post(self, request):
        
        folderName = request.data.get('folderName')
        token = request.data.get('token')
        folderParent = request.data.get('folderParent')
        
        agregar = clientFolder.service.registerFolderSoap(token,folderName,folderParent)
        
        return Response(agregar)
    
    def put(self, request):
        
        folderName = request.data.get('folderName')
        token = request.data.get('token')
        folderId = request.data.get('folderId')
        folderParent = request.data.get('folderParent')
        
        editar = clientFolder.service.updateFolderSoap(token, folderId, folderName, folderParent)
        
        return Response(editar)
    
    def delete(self, request):
        
        token = request.data.get('token')
        folderId = request.data.get('folderId')
        
        eliminar = clientFolder.service.deleteFolderSoap(token, folderId)
        
        return Response(eliminar)
        
#endregion