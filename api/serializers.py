from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Note

class NoteSerializer(ModelSerializer):
    def validate_tags(self, value):
        if value is not None and (
            not isinstance(value, list) or any(not isinstance(tag, str) for tag in value)
        ):
            raise ValidationError('Tags must be an array of strings or null.')
        return value

    class Meta:
        model = Note
        fields = '__all__'
