from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Type, Note, Tag, TagNoteSub, Genealogy
from .serializers import TypeSerializer, NoteSerializer, TagSerializer, TagNoteSubSerializer
from document_service.models import Document


class BaseViewSet(viewsets.ReadOnlyModelViewSet):
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except self.queryset.model.DoesNotExist:
            raise NotFound()  # используем стандартное исключение NotFound
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TypeViewSet(BaseViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [AllowAny]


class NoteViewSet(BaseViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        try:
            note = Note.objects.get(pk=pk)

            # Получение связанных тегов
            related_tag_ids = TagNoteSub.objects.filter(note=note).values_list('tag_id', flat=True)
            related_tags = Tag.objects.filter(id__in=related_tag_ids)

            # Сериализация данных
            note_serializer = NoteSerializer(note)
            tag_serializer = TagSerializer(related_tags, many=True)

            # Формирование кастомного ответа
            custom_response = {
                'note_info': note_serializer.data,
                'related_tags': tag_serializer.data,
            }

            return Response(custom_response)

        except Note.DoesNotExist:
            return Response({'detail': 'Note not found.'}, status=404)

    def create(self, request, *args, **kwargs):
        owner_id = request.data.get('owner_id')
        document_id = request.data.get('document_id')
        type_id = request.data.get('type_id')

        try:
            owner = User.objects.get(pk=owner_id)
            try:
                document = Document.objects.get(pk=document_id)
                try:
                    note_type = Type.objects.get(pk=type_id)
                except Type.DoesNotExist:
                    return Response({"error": f"Type with ID {type_id} does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)

            except Document.DoesNotExist:
                return Response({"error": f"Document with ID {document_id} does not exist"},
                                status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": f"User with ID {owner_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        note = Note.objects.create(
            owner=owner,
            docId=document,
            typeId=note_type,
            subject=request.data.get('subject'),
            payload=request.data.get('payload')
        )
        serializer = self.get_serializer(note)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """
        Частичное обновление заметки.
        """
        note = get_object_or_404(Note, pk=pk)  # Используем get_object_or_404 для краткости

        # Обновляем только переданные поля
        for field in ['subject', 'payload']:
            if field in request.data:
                setattr(note, field, request.data[field])

        # Сохраняем изменения
        note.save()

        # Возвращаем обновленную заметку
        serializer = self.get_serializer(note)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by_tag/(?P<tag_id>[^/.]+)')
    def notes_by_tag(self, request, tag_id):
        """
        Возвращает список заметок, связанных с тегом, по ID тега.
        """
        child_tags = Genealogy.objects.filter(parent_id=tag_id).values_list('child_id', flat=True)
        parent_tags = Genealogy.objects.filter(child_id=tag_id).values_list('parent_id', flat=True)

        notes = self.get_serializer(
            Note.objects.filter(tagnotesub__tag_id=tag_id), many=True
        ).data

        notes_child = {}
        for child_tag_id in child_tags:
            notes_child[child_tag_id] = self.get_serializer(
                Note.objects.filter(tagnotesub__tag_id=child_tag_id), many=True
            ).data

        notes_parent = {}
        for parent_tag_id in parent_tags:
            notes_parent[parent_tag_id] = self.get_serializer(
                Note.objects.filter(tagnotesub__tag_id=parent_tag_id), many=True
            ).data

        return Response({
            'notes': notes,
            'notes_child': notes_child,
            'notes_parent': notes_parent
        })

    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        _note = self.get_object()
        _tag = Tag.objects.get(pk=request.data['tag_id'])
        print(_tag.id)

        tag_note_sub = TagNoteSub.objects.create(
            tag=_tag,
            note=_note
        )
        serializer = TagNoteSubSerializer(tag_note_sub)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_tag(self, request, pk=None):
        note = self.get_object()
        try:
            tag_note_sub = TagNoteSub.objects.get(note_id=note.id, tag_id=request.data['tag_id'])
            tag_note_sub.delete()
            return Response(status=204)
        except TagNoteSub.DoesNotExist:
            return Response({'detail': 'Tag not found on this note.'}, status=404)

    def destroy(self, request, pk=None):
        """
        Удаление заметки.
        """
        try:
            note = Note.objects.get(pk=pk)
            note.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Note.DoesNotExist:
            return Response({'detail': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)


class TagViewSet(BaseViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        tag_counts = TagNoteSub.objects.values('tag_id').annotate(
            count=Count('id')
        ).order_by('-count')

        # Преобразуем QuerySet в словарь для удобства
        tag_counts_dict = {tag['tag_id']: tag['count'] for tag in tag_counts}

        for tag_data in serializer.data:
            tag_data['tag_note_sub_count'] = tag_counts_dict.get(tag_data['id'], 0)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Возвращает тег по его ID.
        """
        try:
            tag = Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return Response({'detail': 'Tag not found.'}, status=404)

        tag_notes = TagNoteSub.objects.filter(tag=pk)
        child_relations = Genealogy.objects.filter(parent=tag)
        parent_relations = Genealogy.objects.filter(child=tag)

        response = {
            'tag_info': {
                'id': tag.id,
                'title': tag.title,
            },
            'related_notes': [
                {
                    'id': tag_note.note.id,
                    'subject': tag_note.note.subject,
                }
                for tag_note in tag_notes
            ],
            'child_tags': [
                {
                    'id': relation.child.id,
                    'title': relation.child.title
                }
                for relation in child_relations
            ],
            'parent_tags': [
                {
                    'id': relation.parent.id,
                    'title': relation.parent.title
                }
                for relation in parent_relations
            ]
        }
        return Response(response)

    @action(detail=True, methods=['patch'])
    def update_relations(self, request, pk=None):
        tag = self.get_object()

        parent_id = request.data.get('parent_id')
        child_id = request.data.get('child_id')

        try:
            if parent_id:
                parent_tag = get_object_or_404(Tag, pk=parent_id)
                Genealogy.objects.create(parent=parent_tag, child=tag)
            if child_id:
                child_tag = get_object_or_404(Tag, pk=child_id)
                Genealogy.objects.create(parent=tag, child=child_tag)

            return Response({'status': 'Отношения тегов обновлены'}, status=status.HTTP_200_OK)

        except Tag.DoesNotExist:
            return Response({'error': 'Указанный тег не найден'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Удаление тега.
        """
        try:
            tag = Tag.objects.get(pk=pk)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response({'detail': 'Tag not found.'}, status=status.HTTP_404_NOT_FOUND)