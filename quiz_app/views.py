from django.shortcuts import render, redirect
from django.views.generic.base import View
from .forms import RegistrationForm,LoginForm,UserProfileForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.http.response import HttpResponseRedirect, HttpResponse
from .send_msg import send_email,send_sms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category,Question,SubmitAnswer,FileUpload,FeedBack,Marksheet,Query,Timing
from django.views.decorators.http import require_POST
import json
from django.db.models.aggregates import Sum,Count
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def home(request):
    return render(request, 'quiz_app/home.html')

class LoginView(View):
    
    def get(self,request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to = '/')
        fm = LoginForm()
        return render(request,'quiz_app/login.html',{'fm' : fm})
    
    def post(self,request):
        fm = LoginForm(data=request.POST)
        if fm.is_valid():
            uname = fm.cleaned_data["username"]
            pw = fm.cleaned_data["password"]
            user = authenticate(username=uname, password=pw)
            if user is not None:
                login(request,user)
                messages.success(request,"Your account successfully logged in!!")
                return HttpResponseRedirect(redirect_to = '/')
            else:
                messages.add_message(request,messages.WARNING,'Please enter a correct username and password')
        return render(request,'quiz_app/login.html',{'fm' : fm})

class RegistrationView(View):
    
    def get(self,request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(redirect_to = '/')
        fm = RegistrationForm()
        return render(request,'quiz_app/registration.html',{'fm' : fm})
    
    def post(self,request):        
        fm = RegistrationForm(request.POST)
        if fm.is_valid():
            fm.save()
            uname = fm.cleaned_data["username"]
            pw = fm.cleaned_data["password2"]
            phone_no = fm.cleaned_data["phone_no"]
            user = authenticate(username=uname, password=pw)
            if user is not None:
                login(request,user)
                messages.success(request,"Your account successfully registered!!")
                domain = request.build_absolute_uri('/')[:-1].split("//")[1]
                send_email('send_email/register_success.html',"Account successfully activated",user.email,username = user.username,domain = domain)
                send_sms(str(phone_no),domain,user.username)
                return HttpResponseRedirect(redirect_to = '/')
        return render(request,'quiz_app/registration.html',{'fm' : fm})

def logout_user(request):
    logout(request)
    messages.success(request,"Your account successfully logged out!!")
    return HttpResponseRedirect("/")

@login_required
def user_profile(request):
    if request.method=="POST":
        fm = UserProfileForm(request.POST,instance=request.user)
        if fm.is_valid():
            fm.save()
            messages.success(request,"Profile Successfully Updated!!!")
            return HttpResponseRedirect("/user/user_profile")
        else:
            for e in fm.errors.as_data():
                messages.success(request,fm.errors[e].as_data()[0])
            return HttpResponseRedirect("/user/user_profile")
            
    else:
        fm = UserProfileForm(instance=request.user)
        user_inst = User.objects.get(id = request.user.id)
    return render(request,"quiz_app/my_profile.html",{"user_inst":user_inst,"us":request.user,"fm":fm})

def get_quetions(request):
    ct = Category.objects.all().order_by("?")
    fetch_question = []
    que_ids = []
    already_ex = request.session.get("que_ids")
    if already_ex:
        ques = Question.objects.filter(id__in = already_ex).order_by("category")
        for ech in ques:
            fetch_question.append(ech)
    else:
        for cat in ct:
            ques = cat.cat_question.all().order_by("?")[:10]
            for ech in ques:
                fetch_question.append(ech)
                que_ids.append(ech.id)
        request.session["que_ids"] = que_ids
    first_question_id = fetch_question[0].id
    question_count  = len(fetch_question)
    all_category = ct
    return all_category,question_count,fetch_question,first_question_id
    

@login_required
def start_pre_quiz(request):
    try:
        if request.user.pre_complete:
            messages.success(request,"You have already submitted pre quiz!! Now start post quiz..")
            return HttpResponseRedirect(redirect_to = "/start_quiz/post/")
        all_category,question_count,fetch_question,first_question_id = get_quetions(request)
        pre_tm = Timing.objects.all().latest('id').pre_time
        return render(request,'quiz_app/start_pre_quiz.html',{"all_category" : all_category,"question_count":question_count,'que' : fetch_question,"first_id" : first_question_id,'pre_time' : pre_tm})
    except Exception:
        messages.success(request,'Something Went Wrong!!Try again later')
        return HttpResponseRedirect(redirect_to = '/')
        

@login_required
def start_post_quiz(request):
    try:
        if request.user.pre_complete:
            if request.user.post_complete:
                messages.success(request,"You have already submitted post quiz!!!")
                return HttpResponseRedirect(redirect_to = "/")
            get_id = request.session.get("ids") or []
            fail_id = request.session.get("fail_id") or []
            if len(get_id) != len(fail_id):
                messages.success(request,'Please Read PPT or PDF or watch full video and then give the post quiz!!')
                return HttpResponseRedirect(redirect_to = '/all_done/pre')
            all_category,question_count,fetch_question,first_question_id = get_quetions(request)
            pre_tm = Timing.objects.all().latest('id').post_time
            return render(request,'quiz_app/start_post_quiz.html',{"all_category" : all_category,"question_count":question_count,'que' : fetch_question,"first_id" : first_question_id,'pre_time' : pre_tm})
        messages.success(request,'Please give the pre quiz first then start post quiz!!')
        return HttpResponseRedirect(redirect_to = '/')
    except Exception:
        messages.success(request,'Something Went Wrong!!Try again later')
        return HttpResponseRedirect(redirect_to = '/')

def fetch_one_quetion(request,pk):
        question = Question.objects.select_related('category').filter(pk=pk).first()
        ctx = {"question" : question.question,
            "op1" : question.option1,
            "op2" : question.option2,
            "op3" : question.option3 if question.option3 else False,
            "op4" : question.option4 if question.option4 else False,
            "category" : question.category.category_name
            }
        return ctx

@login_required
@require_POST
def fetch_pre_questions(request,pk):
    if request.method == 'POST':
        ctx = fetch_one_quetion(request,pk)
        id_list = request.session.get('question_id',[])
        final_submit = Question.objects.exclude(id__in = id_list).exists()
        attempt = False
        if pk in id_list:
            attempt = True
        ctx["attempt"] = attempt
        ctx["final_submit"] = not final_submit
    return HttpResponse(json.dumps(ctx), content_type='application/json')

@login_required
@require_POST
def fetch_post_questions(request,pk):
    if request.method == 'POST':
        ctx = fetch_one_quetion(request,pk)
        id_list = request.session.get('post_question_id',[])
        final_submit = Question.objects.exclude(id__in = id_list).exists()
        attempt = False
        if pk in id_list:
            attempt = True
        ctx["attempt"] = attempt
        ctx["final_submit"] = not final_submit
    return HttpResponse(json.dumps(ctx), content_type='application/json')

@require_POST
@login_required
def checkAns(request,pk,ans,q_type):
    user = request.user
    if request.method == 'POST':
        if q_type == 'post':
            qu_id = request.session.get('post_question_id')
            if qu_id:
                request.session["post_question_id"] = qu_id + [pk]
            else:
                request.session["post_question_id"] = [pk]
            final_submit = Question.objects.exclude(id__in = request.session.get('post_question_id',[])).exists()
        else:
            qu_id = request.session.get('question_id')
            if qu_id:
                request.session["question_id"] = qu_id + [pk]
            else:
                request.session["question_id"] = [pk]
            final_submit = Question.objects.exclude(id__in = request.session.get('question_id',[])).exists()

        question = Question.objects.select_related('category').get(pk=pk)
        is_post = True if q_type == "post" else False
        sub_obj,_ = SubmitAnswer.objects.get_or_create(name = user,category = question.category,is_post_quiz = is_post)
        if ans == question.get_true_ans:
            sub_obj.tru_ans += 1
            sub_obj.total_score += 1
            sub_obj.save()
            currect_qu = request.session.get('get_currect_qu')
            if currect_qu:
                request.session["get_currect_qu"] = currect_qu + [pk]
            else:
                request.session["get_currect_qu"] = [pk]
        else:
            sub_obj.wrong_ans += 1
            sub_obj.save()
            wrong_qu = request.session.get('get_wrong_qu')
            if wrong_qu:
                request.session["get_wrong_qu"] = wrong_qu + [pk]
            else:
                request.session["get_wrong_qu"] = [pk]

    ctx = {'final_submit' : not final_submit,"q_id" : question.id}
    return HttpResponse(json.dumps(ctx), content_type='application/json')    

def all_done_pre_post(request,re_type,user):
    try:
        total_score = 0
        all_sub_ans = SubmitAnswer.objects.filter(name = user,is_post_quiz = re_type).select_related("category")
        test_pass = True if all_sub_ans else False
        fail_id = []
        for ct in all_sub_ans:
            total_score += ct.total_score
            if ct.total_score < 8:
                test_pass = False
                for a_id in ct.category.cat_video.all():
                    fail_id.append(a_id.id)
        request.session["fail_id"] = fail_id  
        out_of = all_sub_ans.aggregate(out_of_marks = Count("category"))
        return test_pass,total_score,all_sub_ans,out_of["out_of_marks"]*10
    except Exception as e:
        pass

@login_required
def alldone(req,re_type):
    user = req.user
    re_types = True if re_type == 'post' else False
    if req.method == 'POST':
        if re_type == 'post':
                User.objects.filter(id=user.id).update(post_complete = True)
                cat = Category.objects.all()  
                for ct in cat: 
                    sab_ans = SubmitAnswer.objects.filter(name = user,is_post_quiz = True,category = ct)
                    if not sab_ans:
                        SubmitAnswer.objects.create(name = user,category = ct,is_post_quiz = True)
        else:
            User.objects.filter(id=user.id).update(pre_complete = True)
            cat = Category.objects.all()  
            for ct in cat: 
                sab_ans = SubmitAnswer.objects.filter(name = user,is_post_quiz = False,category = ct)
                if not sab_ans:
                    SubmitAnswer.objects.create(name = user,category = ct,is_post_quiz = False)
                    fail_id = req.session.get("fail_id") or []
                    for a_id in ct.cat_video.all():
                        fail_id.append(a_id.id)
                    req.session["fail_id"] = fail_id
            try:
                del req.session["que_ids"]
            except Exception:
                pass
            try:
                del req.session["get_wrong_qu"]
            except Exception:
                pass
            try:
                del req.session["get_currect_qu"]
            except Exception:
                pass
        try:
            test_pass,total_score,all_sub_ans,out_of = all_done_pre_post(req,re_types,user)
            send_email('send_email/student_mark.html',f"Your {re_type} quiz marks",user.email,username = user.username,re_type=re_type,all_sub_ans = all_sub_ans)
        except Exception:
            messages.success(req,"You have't attain any question!!!")
            return HttpResponseRedirect(redirect_to = '/')
        return render(req,'quiz_app/all_done.html',{"re_type":re_type,"test_pass":test_pass,"total_score":total_score,"out_of":out_of,"user_name":user.username,"all_sub_ans":all_sub_ans})
    else:
        try:
            test_pass,total_score,all_sub_ans,out_of = all_done_pre_post(req,re_types,user)
        except Exception:
            messages.success(req,"You have't attain any question!!!")
            return HttpResponseRedirect(redirect_to = '/')
        return render(req,'quiz_app/all_done.html',{'re_type' : re_type,"total_score":total_score,"test_pass":test_pass,"out_of":out_of,"user_name":user.username,"all_sub_ans":all_sub_ans})

@login_required
@csrf_exempt
def ppt_pdf_video_seen(request,pk,re_type):
    get_id = request.session.get("ids")
    if re_type == "push":
        if not get_id:
            request.session["ids"] = [pk]
        elif pk not in get_id:
            request.session["ids"] = get_id + [pk]
        return HttpResponse(json.dumps({"id" : pk}), content_type='application/json') 
    else:
        ids = get_id if get_id else False
        return HttpResponse(json.dumps({"ids" : ids}), content_type='application/json') 

@login_required
def show_video(request,cat_name):
    files = FileUpload.objects.filter(category__category_name = cat_name)
    cat = files.first().category
    return render(request,"quiz_app/video_show.html",{"files" : files,"cat" : cat})


@login_required
def show_my_graph(request):
    pre_com = not request.user.pre_complete
    post_com = not request.user.post_complete
    return render(request,"quiz_app/show_graph.html",{"pre_com" : pre_com,"post_com" : post_com})

def get_pr_value(user,is_post):
    _quiz = SubmitAnswer.objects.filter(name = user,is_post_quiz = is_post)
    total_gain = _quiz.aggregate(total_sum = Sum('total_score'))
    total_mark = _quiz.aggregate(total_mark = Count('category'))
    total_pr = (total_gain["total_sum"]*100)/(total_mark['total_mark']*10)
    ctx = {"per_mark" : total_pr}
    return ctx

@login_required
def render_graph(request,user_name):
    _user = User.objects.get(username = user_name)
    pre_com = _user.pre_complete
    post_com = _user.post_complete
    pre_data = False
    post_data = False
    diff_val = False
    if pre_com:
        pre_data = get_pr_value(_user,False)
    if post_com:
        post_data = get_pr_value(_user,True)
    if pre_com and post_com:
        diff_val = post_data['per_mark'] - pre_data["per_mark"]
    data = {"pre_data" : pre_data, "post_data" : post_data,"diff_val" : diff_val}
    return HttpResponse(json.dumps(data), content_type='application/json') 

def cal_admin_graph(is_post):
    cat_set = Category.objects.all()
    cat_dict = {bct.category_name:0 for bct in cat_set}
    for ct in cat_set:
        pre_quiz = SubmitAnswer.objects.filter(category = ct,is_post_quiz = is_post)
        if pre_quiz:
            total_gain = pre_quiz.aggregate(total_sum = Sum('total_score'),total_ct = Count('name'))
            ot = total_gain["total_ct"] * 10
            try:
                total_mark = (total_gain["total_sum"]*100)/ ot
            except ZeroDivisionError:
                total_mark = 0
            cat_dict[ct.category_name] = total_mark
    return cat_dict

@login_required
def admin_graph_show(request,re_type):
    is_post = True if re_type == "post" else False
    if re_type != "both":
        cat_dict = cal_admin_graph(is_post)
        return HttpResponse(json.dumps(cat_dict), content_type='application/json')
    else:
        post_dict = cal_admin_graph(is_post = True)
        pre_dict = cal_admin_graph(is_post = False)
        return HttpResponse(json.dumps({"post_dict" : post_dict,"pre_dict" : pre_dict}), content_type='application/json')

@login_required
def show_all_quetion(request):
    if request.user.post_complete:
        ids = request.session.get("que_ids") or []
        all_questions = Question.objects.filter(id__in = ids).order_by('category')
        currect_qu = request.session.get('get_currect_qu')
        wrong_qu = request.session.get('get_wrong_qu')
        return render(request,'quiz_app/show_all_questions.html',{"all_questions" : all_questions,"currect_qu" : currect_qu,"wrong_qu" : wrong_qu})
    else:
        messages.success(request,"Please give the post quiz!!")
        return HttpResponseRedirect(redirect_to = "/")
    
@login_required
def feed_back_form(request):
    user = request.user
    feed_text = request.POST.get("msg")
    FeedBack.objects.create(user_name = user,feed_back_text = feed_text)
    messages.success(request,"Your Feedback Successfully Submitted!!")
    request.session["feed_back"] = True
    return HttpResponse(json.dumps({"Done" : "Done"}), content_type='application/json') 

import datetime
def forgot_password(request):
    if request.method == "POST" or request.is_ajax():
        email_id = request.POST.get("email_id")
        re_type = request.POST.get("re_type")
        error = False
        if re_type == "otp_send":
            try:
                user = User.objects.get(email = email_id)
            except Exception:
                error = "No any user Found for this given email..."
            if not error:
                otp = datetime.datetime.now().strftime('%f')
                user.user_otp = otp
                user.save(update_fields = ["user_otp"])
                send_email('send_email/forgot_password.html',"OTP Verification for forgot password",user.email,username = user.username,otp = otp)
        elif re_type == "validate":
            otp_val = request.POST.get("otp_val")
            _user = User.objects.filter(email = email_id,user_otp = otp_val).first()
            if _user is None:
                error = "Invalid OTP..Try Again!!!"
            else:
                _user.user_otp = None
                _user.save(update_fields = ["user_otp"])
                login(request,_user,backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request,"Your account successfully logged in!!")
        return HttpResponse(json.dumps({"error" : error}), content_type='application/json') 
    else:
        return render(request,"quiz_app/forgot_password.html")
  
import csv
from io import StringIO
from django.core.files.base import ContentFile

@login_required
def generate_marksheet(request,re_type):
    is_post = True if re_type == 'post' else False 
    colms = Category.objects.all().order_by("category_name").values_list("category_name",flat = True)
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(colms)
    users = User.objects.all()
    for us in users:
        submit_ans = SubmitAnswer.objects.filter(name = us,is_post_quiz = is_post).order_by('category__category_name').values_list('total_score',flat = True)
        csv_writer.writerow(submit_ans)
    csv_file = ContentFile(csv_buffer.getvalue().encode('utf-8'))
    mar_sh = Marksheet(quiz_type = 'post_quiz' if re_type == 'post' else 'pre_quiz' )
    mar_sh.excel_file.save('mark_sheet.csv', csv_file)
    messages.success(request,"Mark Sheet succesfully generated!!!")
    return redirect(request.META['HTTP_REFERER'])

def admin_graph(request):
    return render(request,'admin/marks_graph.html')

def show_quiz_ml_analysis(request,re_type):
    if re_type == 'post':
        return render(request,'admin/post_marks_analysis.html')
    return render(request,'admin/pre_marks_analysis.html')

from .ml import generate_graph
def render_an_graph(request,re_type,cat_name):
    category = Category.objects.all().order_by("category_name")
    file_obj = Marksheet.objects.filter(quiz_type = re_type).latest('cr_date').excel_file
    if file_obj:
        cats = []
        for ct in category:
            cats.append(ct.category_name)
        cat_name = cats[0] if cat_name == 'No' else cat_name
        data = generate_graph(file_obj = file_obj,target_name = cat_name)
        data["category"] = cats
    return HttpResponse(json.dumps(data), content_type='application/json') 

def user_query(request):
    _name = request.POST.get("name_val")
    contact_sr = request.POST.get("contact_sr")
    query_text = request.POST.get("query_text")
    Query.objects.create(u_name = _name,contact_source = contact_sr,query_text = query_text)
    messages.success(request,"Your Query Successfully Submitted!!")
    return HttpResponse(json.dumps({"Done" : "Done"}), content_type='application/json') 

def mrk_cal(is_post):
    _cat = Category.objects.all().order_by("category_name")
    data = []
    for ct in _cat:
        data_dict = {}
        data_dict['cat_name'] = ct.category_name
        data_dict['full_mark'] = 10
        data_dict['half_mark'] = 5
        sb_ans = SubmitAnswer.objects.filter(is_post_quiz = is_post,category = ct).exclude(total_score = 0)
        data_dict['total_student'] = sb_ans.count()
        data_dict['half_st_count'] = sb_ans.filter(total_score__gte = 5).count()
        try:
            count_pr = (data_dict['half_st_count'] * 100) / data_dict['total_student']
        except ZeroDivisionError:
            count_pr = (data_dict['half_st_count'] * 100) / 1
            
        count_pr = round(count_pr, 2)
        data_dict['pr_value'] = count_pr
        if count_pr >= 55:
            data_dict['attainment'] = 3
        elif count_pr >= 40:
            data_dict['attainment'] = 2
        else:
            data_dict['attainment'] = 1
        data.append(data_dict)
    return data

def marks_analysis(request):
    pre_data = mrk_cal(is_post = False)
    post_data = mrk_cal(is_post = True)
    return render(request,'admin/mark_analysis.html',{"pre_data" : pre_data,"post_data" : post_data})

def all_students_marks(request):
    all_us = User.objects.all().order_by('post_complete')
    us_data = []
    for ig in all_us:
        data_dict = {}
        data_dict["user_name"] = ig.username
        data_dict["user_id"] = ig.id
        data_dict["pre_marks"] = ig.submited_ans.filter(is_post_quiz = False).aggregate(t_sum = Sum('total_score')).get('t_sum')
        data_dict["post_marks"] = ig.submited_ans.filter(is_post_quiz = True).aggregate(tp_sum = Sum('total_score')).get('tp_sum')
        us_data.append(data_dict)
    return render(request,"admin/all_students_marks.html",{"all_us" : us_data})