from django.contrib.gis import admin

# Register your models here.
#register worldborder model

from .models import WorldBorder, Square

admin.site.register(WorldBorder,admin.GISModelAdmin)


class SquareAdmin(admin.GISModelAdmin):
    list_display = ('name', 'north', 'south', 'east', 'west')

admin.site.register(Square, SquareAdmin)