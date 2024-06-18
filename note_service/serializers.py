from rest_framework.serializers import ModelSerializer

from .models import Type, Note, Tag, TagNoteSub


class TypeSerializer(ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagNoteSubSerializer(ModelSerializer):
    class Meta:
        model = TagNoteSub
        fields = ['note_id', 'tag_id']

