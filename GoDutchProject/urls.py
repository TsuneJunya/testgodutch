from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView
from GoDutchApp import views
from django.views.decorators.http import require_POST
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', LoginView.as_view(), name='login'),  # 空のパスに LoginView を指定
    path('top/', views.top_view, name='top'),
    # 経費タイトル登録更新画面
    path('expense_regist/', views.expense_regist, name='expense_regist'),
    path('expense_regist/<int:expense_id>/', views.expense_regist, name='expense_regist'),
    # 経費タイトル登録処理
    path('expense_regist_execute/', views.expense_regist_execute, name='expense_regist_execute'),
    path('expense_delete_execute/<int:expense_id>/', views.expense_delete_execute, name='expense_delete_execute'),
    # 経費明細一覧画面
    path('expense_detail_list/<int:expense_id>/', views.expense_detail_list, name='expense_detail_list'),
    # 経費明細登録/更新画面
    path('expense_detail_create/<int:expense_id>/', views.expense_detail_create, name='expense_detail_create'), 
    path('expense_detail_create/<int:expense_id>/<int:detail_id>/', views.expense_detail_create, name='expense_detail_create'), 
    # 経費明細削除処理
    path('delete_expense_detail/<int:expense_id>/<int:detail_id>/', views.delete_expense_detail, name='delete_expense_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),  
    
]