from django.conf import settings

def site(request):
    return {"WHATSAPP": settings.WHATSAPP_NUMBER, "WAVE_NUMBER": settings.WAVE_NUMBER, "WAVE_NAME": settings.WAVE_NAME}
