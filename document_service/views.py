import os

from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Document, DocType
from .serializers import DocumentSerializer, DocTypeSerializer


class DocTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocType.objects.all()
    serializer_class = DocTypeSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, HTTP_STATUS_CODE_404=None, *args, **kwargs):
        print("DOCTYPE")
        try:
            doctype = self.get_object()
        except DocType.DoesNotExist:
            return Response(status_code=HTTP_STATUS_CODE_404)
        serializer = self.get_serializer(doctype)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):

        documents = self.get_queryset()

        serializer = self.get_serializer(documents, many=True)
        serialized_documents = serializer.data
        for document in serialized_documents:
            # Извлекаем имя файла из полного URL
            file_name = document['file'].split('/')[-1]
            # Обновляем поле 'file' так, чтобы оно содержало путь, начинающийся с '/documents/'
            document['file'] = f'/documents/{file_name}'

        return Response(serialized_documents)

    def retrieve(self, request, HTTP_STATUS_CODE_404=None, *args, **kwargs):
        """
        Возвращает информацию о конкретном документе по его ID.
        """
        try:
            document = self.get_object()
        except Document.DoesNotExist:
            return Response(status_code=HTTP_STATUS_CODE_404)
        serializer = self.get_serializer(document)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']
        # Create a new Document instance
        document = Document(file=uploaded_file)

        typeId = request.data.get('TypeId')

        try:
            document.TypeId = DocType.objects.get(pk=typeId)
        except DocType.DoesNotExist:
            print("error:  Type with ID {} does not exist")
            # Обработка ошибки, если тип не найден
            return Response({"error": "DocType with ID {} does not exist".format(typeId)}, status=400)

        # Save the Document instance and return the serialized data
        document.save()
        serializer = self.serializer_class(document)
        return Response(serializer.data)

    def download(self, request, HTTP_STATUS_CODE_400=None, HTTP_STATUS_CODE_404=None, *args, **kwargs):
        try:
            document = self.get_object()
        except Document.DoesNotExist:
            return Response(status_code=HTTP_STATUS_CODE_404)
        if not document.file:
            return Response(status_code=HTTP_STATUS_CODE_400)
        filename = os.path.basename(document.file.name)
        response = FileResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
