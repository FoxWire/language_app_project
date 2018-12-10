from django.contrib import admin
from lang_app.models import Session, Sentence, UserState, Question, QandA, Block


class QandAAdmin(admin.ModelAdmin):
    raw_id_fields = ('question',)


# Register your models here
admin.site.register(Sentence)
admin.site.register(Question)
admin.site.register(UserState)
admin.site.register(Session)
admin.site.register(QandA, QandAAdmin)
admin.site.register(Block)


