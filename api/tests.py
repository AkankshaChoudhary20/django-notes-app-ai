from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient
from .models import Note


class NoteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('api.views.ai.generate_title_and_tags', return_value=None)
    def test_create_preserves_explicit_title_and_tags(self, generate):
        response = self.client.post('/api/notes/create/', {'body': 'Text', 'title': 'My title', 'tags': ['work']}, format='json')
        self.assertEqual(response.status_code, 200)
        note = Note.objects.get()
        self.assertEqual(note.title, 'My title')
        self.assertEqual(note.tags, ['work'])
        generate.assert_not_called()

    def test_invalid_create_does_not_write(self):
        response = self.client.post('/api/notes/create/', {'title': 'x' * 256}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Note.objects.exists())

    def test_invalid_update_returns_validation_error_and_keeps_note(self):
        note = Note.objects.create(body='Keep this', title='Original')
        response = self.client.put(f'/api/notes/{note.id}/update/', {'title': 'x' * 256}, format='json')
        self.assertEqual(response.status_code, 400)
        note.refresh_from_db()
        self.assertEqual(note.title, 'Original')

    def test_missing_notes_return_404(self):
        self.assertEqual(self.client.get('/api/notes/999999/').status_code, 404)
        self.assertEqual(self.client.put('/api/notes/999999/update/', {}, format='json').status_code, 404)
        self.assertEqual(self.client.delete('/api/notes/999999/delete/').status_code, 404)
