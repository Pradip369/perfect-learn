from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe

class CustomUser(AbstractUser):
    username = models.CharField(max_length=40,unique=True)
    email = models.EmailField(max_length = 50,unique=True)   
    phone_no = models.CharField(null=True,blank=True,max_length=13) 
    pre_complete = models.BooleanField(default=False)
    post_complete = models.BooleanField(default=False)
    user_otp = models.CharField(max_length=20,null = True,blank=True,editable=False)

    class Meta:
        verbose_name = "User Profile"

    def __str__(self):
        return '%s' %(self.username)

class Category(models.Model):
    category_name = models.CharField(max_length = 150)
    category_img = models.ImageField(upload_to = 'category_pic',null = True,blank = True)
    category_description = models.TextField(null = True,blank=True)

    def __str__(self):
        return str(self.category_name)
    
    def cate_img(self):
        if self.category_img:
            return mark_safe('<img src="%s" width="100px" height="100px" />' % (self.category_img.url))
    cate_img.short_description = 'Category Image'

class Question(models.Model):
    
    OPTION_CHOICES = [
        ('option1', 'option1'),
        ('option2', 'option2'),
        ('option3', 'option3'),
        ('option4', 'option4'),
    ]
    
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="cat_question")
    question = models.TextField(unique=True)
    option1 = models.CharField(max_length=200,help_text='Required')
    option2 = models.CharField(max_length=201,help_text='Required')
    option3 = models.CharField(max_length=202,null=True,blank=True,help_text='(Optional)')
    option4 = models.CharField(max_length=204,null=True,blank=True,help_text='(Optional)')
    answer = models.CharField(choices=OPTION_CHOICES,max_length=205,help_text='This answer must be match for given above option..')
    solution = models.TextField(blank=True,null=True,help_text='(Optional) If possible! give the specific solution for this question..')
    cr_date = models.DateTimeField(auto_now=True,verbose_name='Created Date')
    
    class Meta:
        verbose_name_plural = "Questions"
    
    @property
    def get_true_ans(self):
        if self.answer == 'option1':
            tru_ans = self.option1
        elif self.answer == 'option2':
            tru_ans = self.option2
        elif self.answer == 'option3':
            tru_ans = self.option3
        elif self.answer == 'option4':
            tru_ans = self.option4
        return tru_ans
                        
    def __str__(self):
        return str(self.question)
    
class SubmitAnswer(models.Model):
    name = models.ForeignKey(to = CustomUser,on_delete=models.CASCADE,related_name='submited_ans')
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    tru_ans = models.IntegerField(default=0,verbose_name = "True Answer")    
    wrong_ans = models.IntegerField(default=0) 
    total_score = models.IntegerField(default=0) 
    is_post_quiz = models.BooleanField(default = False,help_text="If Pre quiz then it's true or if Post quiz then it's false..")
    cr_date = models.DateTimeField(auto_now = True,verbose_name='Submited Date')

    def __str__(self):
        return  '%s' %(self.name)

    class Meta:
        verbose_name_plural = "Submited Answer"

from cloudinary_storage.storage import RawMediaCloudinaryStorage
class FileUpload(models.Model):

    FILE_TYPE = [
        ('VIDEO', 'VIDEO'),
        ('PPT', 'PPT'),
        ('PDF', 'PDF'),
    ]

    category = models.ForeignKey(to = Category,on_delete=models.CASCADE,related_name="cat_video")
    file_type = models.CharField(choices=FILE_TYPE,max_length=70)
    source_file = models.FileField(upload_to = 'category_video',storage = RawMediaCloudinaryStorage(),verbose_name = "Upload File",help_text="File must be VIDEO,PPT or PDF...")
    # source_file = models.FileField(upload_to = 'category_video',verbose_name = "Upload File",help_text="File must be VIDEO,PPT or PDF...")

    def __str__(self):
        return str(self.source_file.name)
    
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Upload File"

class Marksheet(models.Model):
    TEST_CHOICES = [
        ('pre_quiz', 'pre_quiz'),
        ('post_quiz', 'post_quiz'),
    ]
    quiz_type = models.CharField(choices=TEST_CHOICES,max_length=20)
    # excel_file = models.FileField(upload_to = 'excel_file',verbose_name='File Name')
    excel_file = models.FileField(upload_to = 'excel_file',storage = RawMediaCloudinaryStorage(),verbose_name = "Upload Excel File",help_text="File must be Excel..")
    cr_date = models.DateTimeField(auto_now_add = True,verbose_name = "Created Date")
    
    def __str__(self):
        return self.excel_file.name
    
    def save(self,*args,**kwargs):
        super(Marksheet, self).save(*args, **kwargs)

class FeedBack(models.Model):
    user_name = models.ForeignKey(to=CustomUser,on_delete=models.CASCADE,related_name="user_feedback")
    feed_back_text = models.TextField()
    created_date = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        verbose_name = "User Feedback"
    
    def __str__(self):
        return str(self.user_name.username)
    
class Query(models.Model):
    u_name = models.CharField(max_length=50,verbose_name = "Name",null=True,blank=True)
    contact_source = models.CharField(max_length=100)
    query_text = models.TextField()
    cre_date = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = "User Query"

    def __str__(self):
        return str(self.contact_source)
    
class Timing(models.Model):
    pre_time = models.IntegerField(verbose_name = 'Pre Quiz Time',help_text="This time must be in minutes...")
    post_time = models.IntegerField(verbose_name = 'Post Quiz Time',help_text="This time must be in minutes...")

    def __str__(self):
        return '%s(%s)' %(self.pre_time,self.post_time)

    class Meta:
        verbose_name = "Quiz Timing"