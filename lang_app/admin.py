from django.contrib import admin
from lang_app.models import Session, Sentence, UserState, Card, QandA

# Register your models here
admin.site.register(Sentence)
admin.site.register(Card)
admin.site.register(UserState)
admin.site.register(Session)
admin.site.register(QandA)


