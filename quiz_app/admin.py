from django.contrib import admin
from .models import CustomUser,Category,Question,SubmitAnswer,FileUpload,Marksheet,FeedBack,Query,Timing
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ExportMixin


admin.site.site_header = 'Ingenuity Towards Skill Enhancement'
admin.site.site_title = 'Ingenuity Towards Skill Enhancement'
admin.site.index_title = 'Ingenuity Towards Skill Enhancement'

class CustomUserAdmin(UserAdmin,ImportExportModelAdmin):
    
    change_form_template = 'admin/user_form.html'
    
    fieldsets = (
        (None, {'fields': ('username','email','password','pre_complete','post_complete')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','phone_no')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    list_filter = ["last_login","date_joined","is_staff"]
    filter_horizontal = ('groups', 'user_permissions',)
    list_per_page = 10
    list_display_links = list_display
    save_on_top = True
    readonly_fields = ['pre_complete','post_complete','last_login', 'date_joined']
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        user_inst = self.get_object(request,object_id)
        extra_context = {
            "user_name" : user_inst.username,
            "marks" : SubmitAnswer.objects.filter(name = user_inst).order_by("is_post_quiz")
        }
        return super(CustomUserAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

admin.site.register(CustomUser,CustomUserAdmin)

class FileUploadInline(admin.StackedInline):
    model = FileUpload
    ordering = ('-id',)
    readonly_fields = ['id']
    extra = 0
    radio_fields = {'file_type' : admin.HORIZONTAL}
    save_on_top = True

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    
    fieldsets = (
        (_('Category Info'), {'fields': ('category_name','category_img','cate_img','category_description')}),
    )
    
    list_display = ['id','cate_img','category_name']
    search_fields=["id","category_name"]
    list_filter = ["category_name"]
    list_per_page = 10
    ordering = ('-id',)
    readonly_fields = ['cate_img']
    list_display_links = list_display
    inlines = [FileUploadInline]
    save_on_top = True

@admin.register(Question)   
class QuestionAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display= ["id","category","question","cr_date"]
    search_fields=["question","answer","category__category_name"]
    list_filter = ["cr_date"]
    list_display_links = ("question","cr_date")
    list_per_page = 10
    radio_fields = {'answer' : admin.VERTICAL,"category" : admin.HORIZONTAL}
    ordering = ('-cr_date',)
    save_on_top = True

@admin.register(SubmitAnswer)
class SubmitAnswerAdmin(ExportMixin,admin.ModelAdmin):
    list_display= ["name","category","tru_ans","wrong_ans","total_score","is_post_quiz","cr_date"]
    search_fields=["name__username","cr_date","category__category_name"]
    list_filter = ["cr_date",]
    # readonly_fields = ['name','category','tru_ans','wrong_ans','total_score', 'is_post_quiz','cr_date']
    list_display_links = list_display
    list_per_page = 10
    ordering = ('-cr_date',)
    save_on_top = True

@admin.register(FeedBack)
class FeedBackAdmin(ExportMixin,admin.ModelAdmin):
    list_display= ["user_name","created_date","feed_back_text"]
    search_fields=["user_name__username"]
    list_filter = ["created_date",]
    readonly_fields = ['user_name','feed_back_text','created_date']
    list_display_links = list_display
    list_per_page = 10
    ordering = ('-created_date',)
    save_on_top = True

@admin.register(Marksheet)
class MarkSheetAdmin(admin.ModelAdmin):
    change_list_template = "admin/marksheet_list.html"
    list_display= ["id",'quiz_type',"excel_file","cr_date"]

@admin.register(Query)
class QueryAdmin(ExportMixin,admin.ModelAdmin):
    list_display= ["id","u_name","contact_source","query_text","cre_date"]
    search_fields=["contact_source"]
    list_filter = ["cre_date",]
    readonly_fields = list_display
    list_display_links = list_display
    list_per_page = 10
    ordering = ('-cre_date',)

@admin.register(Timing)
class TimingAdmin(admin.ModelAdmin):
    list_display= ["id","pre_time","post_time"]
    list_display_links = list_display