from django import forms
from django.contrib import admin
from .models import Plugin, PluginVersion


def package_name(obj):
    return obj.name
package_name.short_description = 'Package name'


class PluginForm(forms.ModelForm):
  package_name = forms.CharField(label='Package name')

  class Meta:
    model = Plugin


class PluginVersionInline(admin.StackedInline):
    model = PluginVersion


class PluginAdmin(admin.ModelAdmin):
    form = PluginForm
    exclude = ['name']
    inlines = [PluginVersionInline]

    def save_model(self, request, obj, form, change):
        if change:
            obj.name = form.cleaned_data['package_name']

        return super(PluginAdmin, self).save_model(request, obj, form, change)


class PluginVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'major', 'minor', 'micro')


admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginVersion, PluginVersionAdmin)
