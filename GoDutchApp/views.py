# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest
from django.db.models import Max, Sum, F, Value, DecimalField
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
import json
import math
from GoDutchProject import settings
from .forms import ExpenseDetailForm
from .models import T_Expense, T_Burden_User, T_Expense_Detail, User


# =====ログイン関連====
def custom_login_required(view_func):
    @login_required(login_url='login')
    def wrapped(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        return view_func(request, *args, **kwargs)
    return wrapped

@require_POST
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('top')

# =====トップ画面関連=====
@login_required(login_url='login')
def top_view(request):
    username = request.user.username
    user_id = request.user.id
    user = User.objects.get(pk=user_id)
    user_group = user.groups.first()
    user_group_name = user_group.name
    expenses = T_Expense.objects.filter(expense_group_id=user_group.id)
    context = {'username': username, 'expenses': expenses, 'user_group_name': user_group_name}
    return render(request, 'goDutchApp/top.html', context)

# =====登録画面関連=====
def get_user_group_id(request):
    user = request.user
    user_groups = user.groups.all()
    group_ids = [group.id for group in user_groups]
    return group_ids[0] if group_ids else None

def get_users_by_group_id(group_id):
    try:
        group = Group.objects.get(id=group_id)
        users_in_group = group.user_set.all()
        return users_in_group
    except Group.DoesNotExist:
        return None

def expense_regist(request, expense_id=None):
    group_id = get_user_group_id(request)
    user_group_name = get_group_name(request)
    users = get_users_by_group_id(int(group_id))
    burden_user_ids = list(T_Burden_User.objects.filter(expense_id=expense_id).values_list('burden_user_id', flat=True))
    title_query = T_Expense.objects.filter(expense_id=expense_id).values('title')
    title = title_query.first()['title'] if title_query.exists() else ''
    user_ids_with_burden = [item for item in users.values_list('id', flat=True) if item in burden_user_ids]

    context = {
        'users': users,
        'user_ids_with_burden': user_ids_with_burden,
        'title': title,
        'user_group_name': user_group_name,
        'expense_id': expense_id,
    }
    return render(request, 'goDutchApp/expense_regist.html', context)

@csrf_exempt
def expense_regist_execute(request):

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title', '')
        selected_user_ids = data.get('selectedCheckboxes', [])
        expense_id = data.get('expense_id',None)

        if expense_id:
            # 更新の場合
            expense = update_expense(expense_id, title, request)
            # 負担ユーザーを更新する
            errorMsg = update_burden_user(expense, selected_user_ids, request)            
            if errorMsg:
              return JsonResponse({'success': False, 'message': errorMsg}, status=400)
        else:
            # 新規登録の場合
            expense = create_expense(title, request)
            create_burden_users(expense, selected_user_ids, request)

        return JsonResponse({'success': True, 'expense_id': expense.expense_id})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def create_expense(title, request):
    expense = T_Expense()

    max_expense_id = T_Expense.objects.all().aggregate(Max('expense_id'))['expense_id__max']
    max_expense_id = max_expense_id if max_expense_id is not None else 0

    expense.expense_id = max_expense_id + 1
    expense.expense_group_id = get_user_group_id(request)
    expense.title = title

    username = request.user.username
    expense.create_user = username
    expense.update_user = username

    expense.save()

    return expense

def update_expense(expense_id, title, request):
    expense = get_object_or_404(T_Expense, expense_id=expense_id)

    # 更新
    expense.title = title
    expense.update_user = request.user.username
    expense.save()

    return expense

def create_burden_users(expense, selected_user_ids, request):
    expense_instance = get_object_or_404(T_Expense, expense_id=expense.expense_id)

    for user_id in selected_user_ids:
        T_Burden_User.objects.create(
            expense=expense_instance,
            burden_user_id=user_id,
            create_user=request.user.username,
            update_user=request.user.username,
        )

@csrf_exempt
def update_burden_user(expense, selected_user_ids, request):
    
  expense_id=expense.expense_id

  #該当Expense_Detailからpayerを取得
  payer_ids = T_Expense_Detail.objects.filter(expense_id=expense_id).values('payer')
  print(payer_ids)
  print(selected_user_ids)
  errorMsg = None
  # payer_ids にある payer が selected_user_ids にない場合エラー
  for payer_id in payer_ids:
    if str(payer_id['payer']) not in selected_user_ids:
      errorMsg = 'エラー:支払者は割り勘要員から削除できません。'
      return errorMsg
 
  T_Burden_User.objects.filter(expense=expense).delete()
  create_burden_users(expense, selected_user_ids, request)
  return errorMsg

    
@csrf_exempt
def expense_delete_execute(request, expense_id):
    if request.method == 'POST':
        try:
            # 該当のオブジェクトを取得
            expense = T_Expense.objects.get(expense_id=expense_id)
                       
            if expense:    
                expense_detail = T_Expense_Detail.objects.filter(expense_id=expense_id)
                burden = T_Burden_User.objects.filter(expense_id=expense_id)
                                                      
                # 削除
                expense.delete()
                expense_detail.delete()
                burden.delete()

                # 成功時のレスポンス
                return JsonResponse({'success': True, 'message': '削除が成功しました。'})
            else:
                # Expenseが存在しない場合
                return JsonResponse({'success': False, 'message': '指定されたエクスペンスが見つかりません。'})

        except Exception as e:
            # エラーが発生した場合のレスポンス
            return JsonResponse({'success': False, 'message': str(e)})

    else:
        # POSTメソッド以外のリクエストが来た場合のレスポンス
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


#=====詳細一覧画面関連===== 
def expense_detail_list(request, expense_id):
    user_group_name = get_group_name(request)
    
    # 各テーブルからデータを取得
    expense = T_Expense.objects.filter(expense_id=expense_id).first()
    expense_details = T_Expense_Detail.objects.filter(expense_id=expense_id)
    
    title = expense.title

    # 負担者ごとのユーザー名を取得
    burden_usernames = {}
    for burden_user in T_Burden_User.objects.filter(expense_id=expense_id):
        user_id = burden_user.burden_user_id
        username = User.objects.get(id=user_id).username
        burden_usernames[user_id] = username

    # 同一 expense_id の payment_amount を合計する
    total_payment_amount = T_Expense_Detail.objects.filter(expense_id=expense_id).aggregate(Sum('payment_amount'))['payment_amount__sum']

    # 同一 expense_id の 負担者人数
    total_member_count = T_Burden_User.objects.filter(expense_id=expense_id).count()

    # total_payment_amountがNoneまたは0の場合に0をセット
    total_payment_amount = total_payment_amount or 0

    # ゼロ割りを避ける
    average_payment_amount = math.floor(total_payment_amount / total_member_count) if total_member_count != 0 else 0
    
    # # 支払精算結果データ作成
    payments_data = calculate_each_person_expense(expense_id)
    sorted_payments_data = dict(sorted(payments_data.items(), key=lambda item: item[1], reverse=True))
    people = list(sorted_payments_data.keys())
    paymentsTxt = split_expenses(people, sorted_payments_data)
    
    # テンプレートに渡すコンテキストを作成
    context = {
        'title':title,
        'user_group_name':user_group_name,
        'expense_details': expense_details,
        'burden_usernames': burden_usernames,
        'expense_id': expense_id,
        'total_payment_amount': total_payment_amount,
        'average_payment_amount': average_payment_amount,
        'paymentsTxt':paymentsTxt,
    }

    return render(request, 'goDutchApp/expense_detail_list.html', context)

#=====詳細画面関連=====
def expense_detail_create(request, expense_id, detail_id=None):
    user_group_name = get_group_name(request)
    
    expense_instance = get_object_or_404(T_Expense, expense_id=expense_id)

    updateDoneFlg = False

    if detail_id:
        # 更新モード
        expense_detail = get_object_or_404(T_Expense_Detail, id=detail_id)
    else:
        # 登録モード
        expense_detail = T_Expense_Detail(expense_id=expense_id)

    # Retrieve burden users associated with the expense and include related user field
    burden_user_ids = T_Burden_User.objects.filter(expense_id=expense_id).values('burden_user_id')
    # フィールドがリスト内のいずれかの値と一致する場合
    burden_user_info = User.objects.filter(id__in=burden_user_ids)

    form = ExpenseDetailForm(request.POST or None, instance=expense_detail)

    if request.method == 'POST':
        if form.is_valid():
            expense_detail = form.save(commit=False)
            expense_detail.expense = expense_instance
            expense_detail.save()
            updateDoneFlg = True
        else:
            print(form.errors)
            return HttpResponseBadRequest("Form validation failed. Check the form errors.")
    else:
        form = ExpenseDetailForm(instance=expense_detail)
        
    context = {
        'form': form,
        'expense_instance': expense_instance,
        'title': expense_instance.title,
        'user_group_name':user_group_name,
        'expense_detail_list': reverse('expense_detail_list', args=[expense_instance.expense_id]),
        'burden_user_info': burden_user_info, 
        'detail_id':detail_id
    }

    if updateDoneFlg:
        expense_details = T_Expense_Detail.objects.filter(expense_id=expense_id)
        return render(request, 'goDutchApp/expense_detail_list.html', {'expense_details': expense_details, 'expense_id': expense_id})
    else:
        return render(request, 'goDutchApp/expense_detail_create.html', context)
    
@csrf_exempt
def delete_expense_detail(request, expense_id, detail_id):
    if request.method == 'POST':
        expense_detail = get_object_or_404(T_Expense_Detail, id=detail_id)
        expense_detail.delete()

        # 削除後に該当expense_idの一覧画面にリダイレクト
        return redirect('expense_detail_list', expense_id=expense_id)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


#ユーザのグループ名を取得
def get_group_name(request):
    # ユーザーIDを取得
    user_id = request.user.id
    user = User.objects.get(pk=user_id)

    # ユーザーが所属しているグループを取得
    user_group = user.groups.all().first()
    user_group_name = user_group.name

    return user_group_name

#参加者と参加者の立替金額データ作成
def calculate_each_person_expense(expense_id):
    # expense_idに対応するburden_user_idのリストを取得
    burden_user_ids = T_Burden_User.objects.filter(expense_id=expense_id).values_list('burden_user_id', flat=True)

    # burden_user_idsに対応するUserオブジェクトを取得
    users = User.objects.filter(id__in=burden_user_ids).values('id', 'username')
    inti_users_expense = []
    for user in users:
      user_id = user.get('id')  # 辞書から'id'を取得する。存在しない場合はNoneが返る
      inti_users_expense.append({
        'id': user_id,
        'username': user['username'],
        'total_payment': 0
      })
    
    # 各payerに対するtotal_paymentを計算し、結果の辞書を作成
    expenses = T_Expense_Detail.objects.filter(expense_id=expense_id).values(
      'payer', 'payer__username'
    ).annotate(total_payment=Sum('payment_amount'))

    for user_expense in inti_users_expense:
     for expense in expenses:
        if user_expense['id'] == expense['payer'] and user_expense['username'] == expense['payer__username']:
          user_expense['total_payment'] = expense['total_payment']
          break

    # 辞書を作成
    payment_data = {item['username']: item['total_payment'] for item in inti_users_expense}
    return payment_data

#参加者と参加者の立替金額をもとに、各参加者の支払い金額算出し、メッセージで返却
def split_expenses(people, payments):
    total_cost = sum(payments.values())
    num_people = len(people)
    
    if num_people == 0:
        return
    
    average_cost = total_cost / num_people

    # 各参加者の支払い金額を計算
    details = [(person, average_cost - payments.get(person, 0)) for person in people]

    # 支払いの詳細を整形して出力
    payerOutput = []
    receiverOutput = []

    for person, amount in details:
        if amount < 0:
            receiverOutput.append((person, -amount))
        elif amount > 0:
            while amount > 0:
                if not receiverOutput:
                    # receiverOutputが空の場合の処理
                    break
                
                receiver, owed_amount = receiverOutput.pop(0)
                payment = min(amount, owed_amount)
                # payerOutput.append(f"{person}➡︎{receiver}（{payment:.0f}円）")
                payerOutput.append(f"{person}➡︎{receiver}（{'{:,.0f}'.format(payment)}円）")
                amount -= payment
                if owed_amount > payment:
                    receiverOutput.insert(0, (receiver, owed_amount - payment))

    return payerOutput