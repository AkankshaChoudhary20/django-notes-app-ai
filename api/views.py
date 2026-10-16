from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import NoteSerializer
from .models import Note
from . import ai

# Create your views here.

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/notes/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of notes'
        },
        {
            'Endpoint': '/notes/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single note object'
        },
        {
            'Endpoint': '/notes/create/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates new note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/update/',
            'method': 'PUT',
            'body': {'body': ""},
            'description': 'Creates an existing note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/delete/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes and exiting note'
        },
    ]
    return Response(routes)

@api_view(['GET'])
def getNotes(request):
    notes = Note.objects.all().order_by('-created')
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getNote(request, pk):
    note = get_object_or_404(Note, id=pk)
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
def updateNote(request, pk):
    note = get_object_or_404(Note, id=pk)
    serializer = NoteSerializer(instance=note, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteNote(request, pk):
    note = get_object_or_404(Note, id=pk)
    note.delete()
    return Response('Note was deleted!')

@api_view(['POST'])
def createNote(request):
    data = request.data
    serializer = NoteSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    note = serializer.save()
    if not note.title and note.body:
        result = ai.generate_title_and_tags(note.body)
        if result:
            note.title = result.title
            note.tags = result.tags
            note.save()
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def regenerateTitleTags(request, pk):
    try:
        note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found'}, status=404)
    result = ai.generate_title_and_tags(note.body)
    if not result:
        return Response({'error': 'AI title/tag generation unavailable'}, status=503)
    note.title = result.title
    note.tags = result.tags
    note.save()
    return Response(NoteSerializer(note).data)

@api_view(['POST'])
def summarizeNote(request, pk):
    try:
        note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found'}, status=404)
    summary = ai.summarize_note(note.body)
    if summary is None:
        return Response({'error': 'Summarization unavailable'}, status=503)
    return Response({'summary': summary})

@api_view(['POST'])
def improveNote(request, pk):
    try:
        note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found'}, status=404)
    suggestion = ai.improve_writing(note.body)
    if suggestion is None:
        return Response({'error': 'Improve writing unavailable'}, status=503)
    return Response({'suggestion': suggestion})

@api_view(['GET'])
def searchNotes(request):
    query = request.GET.get('q', '')
    notes = list(Note.objects.all().order_by('-created'))
    ids = ai.search_notes(query, notes)
    if ids is None:
        return Response({'error': 'Search unavailable'}, status=503)
    by_id = {n.id: n for n in notes}
    ordered = [by_id[i] for i in ids if i in by_id]
    return Response(NoteSerializer(ordered, many=True).data)

@api_view(['POST'])
def askNotes(request):
    question = request.data.get('question', '')
    notes = list(Note.objects.all().order_by('-created'))
    result = ai.ask_notes(question, notes)
    if result is None:
        return Response({'error': 'Ask unavailable'}, status=503)
    by_id = {n.id: n for n in notes}
    cited = [by_id[i] for i in result.cited_note_ids if i in by_id]
    return Response({
        'answer': result.answer,
        'cited_notes': NoteSerializer(cited, many=True).data,
    })