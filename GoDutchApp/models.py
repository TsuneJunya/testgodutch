from django.db import models
from django.contrib.auth.models import User,Group
from django.shortcuts import render, redirect, get_object_or_404

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_group_id = models.IntegerField()

class T_Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    expense_group_id = models.IntegerField()
    title = models.CharField(max_length=255)
    create_on = models.DateTimeField(auto_now_add=True)
    create_user = models.CharField(max_length=255)
    update_on = models.DateTimeField(auto_now=True)
    update_user = models.CharField(max_length=255)
    update_cnt = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title}"

class T_Burden_User(models.Model):
    burden_id = models.AutoField(primary_key=True)
    expense = models.ForeignKey(T_Expense, on_delete=models.CASCADE)
    burden_user_id = models.IntegerField()
    create_on = models.DateTimeField(auto_now_add=True)
    create_user = models.CharField(max_length=255)
    update_on = models.DateTimeField(auto_now=True)
    update_user = models.CharField(max_length=255)
    update_cnt = models.IntegerField(default=0)
    delete_flg = models.BooleanField(default=False)
        
class T_Expense_Detail(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('0', '現金'),
        ('1', 'カード'),
        ('2', 'PayPay'),
        ('3', 'au pay'),
        ('4', 'Suica'),
    ]
    
    CATEGORY_CHOICES = [
        ('0', '飲食代'),
        ('1', '施設利用料'),
        ('2', 'ガソリン代'),
        ('3', '高速代'),
        ('4', '宿泊代'),
        ('5', '交通費'),
        ('6', '備品代'),
        ('7', '消耗品代'),
        ('8', 'その他'),
    ]

    expense = models.ForeignKey(T_Expense, on_delete=models.CASCADE)  
    payment_on = models.DateField(null=True, verbose_name="支払日") 
    payment_amount = models.DecimalField(max_digits=10, decimal_places=0, null=True, verbose_name="支払金額")
    payer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="支払者")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, null=True,verbose_name="商品種別")
    payee = models.CharField(max_length=20,null=True, blank=True,verbose_name="支払先")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True, verbose_name="支払方法")
    memo = models.CharField(max_length=20, blank=True, null=True, verbose_name="メモ")
    

    