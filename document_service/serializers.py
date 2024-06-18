from rest_framework.serializers import ModelSerializer

from .models import Document, DocType


class DocTypeSerializer(ModelSerializer):
    class Meta:
        model = DocType
        fields = '__all__'


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'TypeId']

    @staticmethod
    def get_file(obj):
        if obj.file:
            return '/documents/' + obj.file.name
        return None
