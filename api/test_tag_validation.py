from django.test import SimpleTestCase
from .serializers import NoteSerializer

class TagValidationTests(SimpleTestCase):
    def test_non_string_lists_and_non_arrays_are_rejected(self):
        for tags in ['work', {'work': True}, [1], [None], [['nested']]]:
            serializer = NoteSerializer(data={'body': 'A note', 'tags': tags})
            self.assertFalse(serializer.is_valid(), tags)
            self.assertIn('tags', serializer.errors)

    def test_arrays_null_and_omitted_tags_remain_supported(self):
        for data in [{'tags': ['work', 'ideas']}, {'tags': []}, {'tags': None}, {}]:
            serializer = NoteSerializer(data={'body': 'A note', **data})
            self.assertTrue(serializer.is_valid(), serializer.errors)
