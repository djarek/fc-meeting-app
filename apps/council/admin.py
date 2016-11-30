from django.contrib import admin
import apps.council.models as council_models


admin.site.register(council_models.FacultyCouncil)
admin.site.register(council_models.FacultyCouncilMember)
admin.site.register(council_models.Meeting)
admin.site.register(council_models.Person)
admin.site.register(council_models.Point)
admin.site.register(council_models.Resolution)
admin.site.register(council_models.ResolutionPoint)
admin.site.register(council_models.VoteOutcome)
admin.site.register(council_models.Invited)
