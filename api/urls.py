from django.urls import path
from .views import *

urlpatterns = [
    path('', getRoutes, name="routes"),
    path('notes/', getNotes, name="notes"),
    # Single-segment literal routes must come before the notes/<pk>/ catch-all below,
    # or e.g. GET /notes/search/ would resolve as getNote(pk="search").
    path('notes/search/', searchNotes, name="search-notes"),
    path('notes/ask/', askNotes, name="ask-notes"),
    path('notes/create/', createNote, name="create-note"),
    path('notes/<str:pk>/update/', updateNote, name="update-note"),
    path('notes/<str:pk>/delete/', deleteNote, name="delete-note"),
    path('notes/<str:pk>/summarize/', summarizeNote, name="summarize-note"),
    path('notes/<str:pk>/improve/', improveNote, name="improve-note"),
    path('notes/<str:pk>/regenerate-tags/', regenerateTitleTags, name="regenerate-tags"),
    path('notes/<str:pk>/', getNote, name="note"),
]