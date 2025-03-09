from django.contrib import admin
from .models import Profile, User, Message, TravelPlan

class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]

@admin.register(TravelPlan)
class TravelPlanAdmin(admin.ModelAdmin):
    list_display = ('destination', 'user', 'duration', 'is_saved', 'created_at')
    list_filter = ('is_saved', 'destination', 'created_at')
    search_fields = ('destination', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'destination', 'duration', 'budget', 'interests', 'group_type', 'is_saved')
        }),
        ('AI-Generated Content', {
            'fields': ('places_to_visit', 'activities', 'restaurants', 'best_time_to_visit', 'itinerary', 'packing_checklist')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Message)


