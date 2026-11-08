from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from glossary.serializers import TextAnalysisInputSerializer
from glossary.services.text_processing import analyse_text


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Liveness probe – confirms the server process is running."""
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def analyse_text_view(request):
    """
    Analyse submitted text and return word frequencies.
    Accepts JSON {"text": "..."} and returns word counts sorted by
    frequency descending, then alphabetically for ties.
    """
    serializer = TextAnalysisInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = analyse_text(serializer.validated_data["text"])
    return Response(result, status=status.HTTP_200_OK)
