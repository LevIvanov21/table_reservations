from django.contrib import admin
from restaurant.models import Table, Booking, ContentText, ContentImage, ContentParameters, Contentlink, Questions, \
    Review


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "places", "flour", "description", )
    list_filter = ("number", )
    search_fields = ("number", "description", )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "table", "places", "notification", "date_field", "time_start", "time_end", "active",
                    "created_at")
    list_filter = ("user", "table", "date_field", "time_start")
    search_fields = ("user", "table")


@admin.register(ContentImage)
class ContentImageAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "image",)
    list_filter = ("title",)
    search_fields = ("title", "description")


@admin.register(ContentText)
class ContentTextAdmin(admin.ModelAdmin):
    list_display = ("title", "body", )
    list_filter = ("title", )
    search_fields = ("title", "body", )


@admin.register(ContentParameters)
class ContentParametersAdmin(admin.ModelAdmin):
    list_display = ("title", "body", "description", )
    list_filter = ("title", )
    search_fields = ("title", "body", )


@admin.register(Contentlink)
class ContentlinkAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "link", "description",)
    list_filter = ("title",)
    search_fields = ("title", "text", "link",)


@admin.register(Questions)
class QuestionsAdmin(admin.ModelAdmin):
    list_display = ("sign", "question_text", "moderated", "answer_text", "created_at",)
    list_filter = ("created_at",)
    search_fields = ("sign", "moderated", "question_text",)


@admin.register(Review)
class ReviewAmin(admin.ModelAdmin):
    list_display = ("author", "review_text", "moderated", "grade", "moderated", "answer_text", "created_at",)
    list_filter = ("created_at",)
    search_fields = ("author", "grade", "moderated",)
