from django.db import models
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.db.models import Count  
from django.contrib.auth.models import User

# Create your models here.

class SystemMinusTax(models.Model):
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'نسبة'),
        ('value', 'قيمة'),
    ]
    CHOICE_FIELD_COASR = [
        ('total_price', 'السعر بدون مصروفات'),
        ('total_invoice_cost','السعر شامل المصروفات'),
    ]
    minus_tax = models.CharField(max_length=100, verbose_name='ضريبة الخصم')
    minus_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name='نوع الضريبة', default='percent')
    choice_field_coast =  models.CharField(max_length=20, choices=CHOICE_FIELD_COASR, verbose_name='ربط الحقول', default='total_invoice_cost')
    percent_minus_tax = models.DecimalField(null=True, blank=True,max_digits=3, decimal_places=2, verbose_name='نسبة الضريبة')
    value_minus_tax = models.FloatField(null=True, blank=True, verbose_name='قيمة الضريبة')
    
    def __str__(self):
         return f"{self.minus_tax} نسبة الضريبة: {self.percent_minus_tax} قيمة الضريبة: {self.value_minus_tax}"
    
    def save(self, *args, **kwargs):
        # إخفاء حقل القيمة إذا تم اختيار النسبة
        if self.minus_type == 'percent':
            self.value_minus_tax = None
        # إخفاء حقل النسبة إذا تم اختيار القيمة
        elif self.minus_type == 'value':
            self.percent_minus_tax = None
        super().save(*args, **kwargs)
    
class SystemAdditionTax(models.Model):
    
    ADDITION_TYPE_CHOICES = [
        ('percent', 'نسبة'),
        ('value', 'قيمة'),
    ]
    CHOICE_FIELD_COASR = [
        ('total_price', 'السعر بدون مصروفات'),
        ('total_invoice_cost','السعر شامل المصروفات'),
    ]
    addition_tax = models.CharField(max_length=100, verbose_name='ضريبة الاضافة')
    addition_type = models.CharField(max_length=20, choices=ADDITION_TYPE_CHOICES, verbose_name='نوع الضريبة', default='percent')
    choice_field_coast =  models.CharField(max_length=20, choices=CHOICE_FIELD_COASR, verbose_name='ربط الحقول', default='total_invoice_cost')
    percent_addition_tax = models.DecimalField(null=True, blank=True, max_digits=3, decimal_places=2, verbose_name='نسبة الضريبة')
    value_addition_tax = models.FloatField(null=True, blank=True, verbose_name='قيمة الضريبة')

    def __str__(self):
        return f"{self.addition_tax} نسبة الضريبة: {self.percent_addition_tax} قيمة الضريبة: {self.value_addition_tax}"
    
    def save(self, *args, **kwargs):
        # إخفاء حقل القيمة إذا تم اختيار النسبة
        if self.addition_type == 'percent':
            self.value_addition_tax = None
        # إخفاء حقل النسبة إذا تم اختيار القيمة
        elif self.addition_type == 'value':
            self.percent_addition_tax = None
        super().save(*args, **kwargs)

class AssetGroup(models.Model):
    asset_group = models.CharField(max_length=100, verbose_name='تصنيف')
    
    def __str__(self):
        return self.asset_group

class Branch(models.Model):
    branch_name = models.CharField(null=True, blank= True, max_length=100, verbose_name='اسم الفرع')
    
    def __str__(self):
        return self.branch_name 
   
class AssetInvoice(models.Model):
    invoice_number = models.CharField(max_length=50, null=True, blank= True, verbose_name='رقم الفاتورة')
    invoice_date = models.DateField(default=timezone.now, null=True, blank= True, verbose_name='تاريخ الفاتورة')
    company_name = models.CharField(max_length=100, null=True, blank= True, verbose_name='اسم المورد')
    supplier_phone = models.CharField(max_length=20, null=True, blank= True, verbose_name='تليفون المورد')
    supplier_address = models.CharField(max_length=200, null=True, blank= True, verbose_name='عنوان المورد')
    total_price = models.FloatField(null=True, blank= True, verbose_name='اجمالي الاسعار')
    
    total_addition_tax = models.FloatField(null=True, blank= True, verbose_name='اجمالي ضريبة الاضافة')
    total_minus_tax = models.FloatField(null=True, blank= True, verbose_name='اجمالي ضريبة النقص')
    total_expences_cost = models.FloatField(null=True, blank= True, verbose_name='اجمالي المصروفات')

    total_invoice_cost = models.FloatField(null=True, blank= True, verbose_name='اجمالي الفاتورة')
    amount_paid = models.FloatField(null=True, blank= True, verbose_name='المدفوع ')
    remaining_balance = models.FloatField(null=True, blank= True, verbose_name='المتبقي ')
    branch_name = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='الفرع')
    invoice_image = models.ImageField(upload_to='invoice_images/', null=True, blank= True)
    invoice_pdf = models.FileField(upload_to='invoices/', null=True, blank= True)
    
    supplier_name = models.CharField(max_length=100, null=True, blank= True, verbose_name='اسم المحول الية')
    id_card_number = models.CharField(max_length=100, null=True, blank= True, verbose_name='رقم البطاقة الشخصية')
    commercial_record = models.CharField(max_length=100, null=True, blank= True, verbose_name='سجل تجاري')
    tax_card = models.CharField(max_length=100, null=True, blank= True, verbose_name='بطاقة ضريبية')
    bank_account_number_to = models.CharField(max_length=100, null=True, blank= True, verbose_name='رقم الحساب')
    bank_name_to = models.CharField(max_length=100, null=True, blank= True, verbose_name='اسم البنك')
    bank_account_number_from = models.CharField(max_length=100, null=True, blank= True, verbose_name='رقم الحساب')
    bank_name_from = models.CharField(max_length=100, null=True, blank= True, verbose_name='اسم البنك')
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def get_absolute_url(self):
        return reverse('invoice-update', kwargs={'pk': self.pk})
    
    def __str__(self):
        #return f"{self.invoice_number} {self.supplier_name} {self.invoice_date} {self.branch_name}"
        return f"({self.invoice_number}) {self.invoice_date}"
    
    @property
    def total_items(self):
        return AssetItems.objects.filter(invoice_number=self).aggregate(Count('asset_number'))['asset_number__count']

class AssetItems(models.Model):
    class Meta:
        ordering = ['invoice_number']
    invoice_number = models.ForeignKey(AssetInvoice, on_delete=models.CASCADE, verbose_name='رقم الفاتورة')
    asset_number = models.CharField(max_length=50, verbose_name='رقم الاصل')
    asset_name = models.CharField(max_length=100, verbose_name='اسم الاصل')
    asset_group = models.ForeignKey(AssetGroup, on_delete=models.PROTECT, verbose_name='تصنيف')
    asset_description = models.CharField(max_length=200, verbose_name='البيان')
    destruction_percent=models.FloatField(verbose_name='نسبة الاهلاك', default=0.10)
    destruction_value=models.FloatField(verbose_name='قيمة الاهلاك', default=1)
    destruction_start_month = models.DateField(default=timezone.now, null=True, blank=True, verbose_name='بداية الاهلاك')
    destruction_end_month = models.DateField(default=timezone.now, null=True, blank=True, verbose_name='نهاية الاهلاك')
    count = models.FloatField(verbose_name='عدد', default=1)
    price = models.FloatField(verbose_name='السعر', default=0)
    asset_price = models.FloatField(verbose_name='سعر الاصل')
    branch_name = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='الفرع')
    
    def __str__(self):
        #return self.asset_number
        return f"{self.asset_number} {self.asset_name}"
    
    @property
    def total_destruction(self):
        return Destruction.objects.filter(asset_item=self).aggregate(Count('destruction_value'))['destruction_value__count']
   
class SystemExpensesCost(models.Model):
    system_expenses_cost = models.CharField(max_length=100, verbose_name='اسم المصروف')
    def __str__(self):
        return self.system_expenses_cost
     
class AdditionTax(models.Model):
    invoice_number = models.ForeignKey(AssetInvoice, on_delete=models.CASCADE, verbose_name='رقم الفاتورة')
    addition_tax = models.ForeignKey(SystemAdditionTax, on_delete=models.PROTECT, verbose_name='نظام ضريبة الاضافة')
    value_tax_increase = models.FloatField(null=True, blank= True, verbose_name='قيمة ضريبة الاضافة')
    
    def __str__(self):
        return f"{self.invoice_number} {self.addition_tax}"
        
class MinusTax(models.Model):
    invoice_number = models.ForeignKey(AssetInvoice, on_delete=models.CASCADE, verbose_name='رقم الفاتورة')
    minus_tax = models.ForeignKey(SystemMinusTax, on_delete=models.PROTECT, verbose_name='نظام ضريبة الخصم')
    value_tax_decrease = models.FloatField(null=True, blank= True, verbose_name='قيمة ضريبة الخصم')
    
    def __str__(self):
        return f"{self.invoice_number} {self.minus_tax}"
    
class ExpensesCost(models.Model):
    invoice_number = models.ForeignKey(AssetInvoice, on_delete=models.CASCADE, verbose_name='رقم الفاتورة')
    expenses_cost = models.ForeignKey(SystemExpensesCost, on_delete=models.PROTECT, verbose_name='تكلفة المصروفات')
    value_expenses_cost = models.FloatField(null=True, blank= True, verbose_name='قيمة المصروف')
    
    def __str__(self):
        return f"{self.invoice_number} {self.expenses_cost}"

class Destruction(models.Model):
    asset_item = models.ForeignKey(AssetItems, on_delete=models.CASCADE, verbose_name='رقم الاصل', default=1)
    destruction_start_month = models.DateField(default=timezone.now, null=True, blank=True, verbose_name='بداية الاهلاك')
    destruction_end_month = models.DateField(default=timezone.now, null=True, blank=True, verbose_name='نهاية الاهلاك')
    destruction_percent = models.FloatField(verbose_name='نسبة الاهلاك')
    destruction_value = models.FloatField(verbose_name='قيمة الاهلاك')
    branch_name = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name='الفرع')
    
    def __str__(self):
        return f"{self.pk} {self.asset_item} {self.destruction_value}"
    
class Transfer(models.Model):
    asset = models.ForeignKey(AssetItems, on_delete=models.CASCADE, verbose_name='الأصل')
    source_branch = models.ForeignKey(Branch, related_name='source_transfers', on_delete=models.CASCADE, verbose_name='الفرع المصدر', blank=True, null=True)
    destination_branch = models.ForeignKey(Branch, related_name='destination_transfers', on_delete=models.CASCADE, verbose_name='الفرع الهدف')
    transfer_date = models.DateField(default=timezone.now, verbose_name='تاريخ التحويل')
    transfer_title = models.CharField(max_length=100, verbose_name='بيان التحويل')
    

    
    def __str__(self):
        return f"{self.asset} - {self.source_branch} to {self.destination_branch}"

class TransferAsset(models.Model):
    transfer_asset = models.ForeignKey(Transfer, on_delete=models.CASCADE, verbose_name='التحويل')
    asset = models.ForeignKey(AssetItems, on_delete=models.CASCADE, verbose_name='الأصل')
    source_branch_asset = models.ForeignKey(Branch, related_name='source_transfers_asset', on_delete=models.CASCADE, verbose_name='الفرع المصدر')
    destination_branch_asset = models.ForeignKey(Branch, related_name='destination_transfers_asset', on_delete=models.CASCADE, verbose_name='الفرع الهدف')
    transfer_date_asset = models.DateField(default=timezone.now, verbose_name='تاريخ التحويل')
    
    def __str__(self):
        return f"{self.transfer_asset} - {self.source_branch_asset} to {self.destination_branch_asset}"
    
class TransferDestructionDetails(models.Model):
    transfer_destruction = models.ForeignKey(Transfer, on_delete=models.CASCADE, verbose_name='التحويل')
    asset = models.ForeignKey(AssetItems, on_delete=models.CASCADE, verbose_name='الأصل')
    destruction = models.ForeignKey(Destruction,related_name='destination_transfers_key', on_delete=models.CASCADE, verbose_name='رقم الاهلاك')
    source_branch_destruction = models.ForeignKey(Branch, related_name='source_transfers_destruction', on_delete=models.CASCADE, verbose_name='الفرع المصدر')
    destination_branch_destruction = models.ForeignKey(Branch, related_name='destination_transfers_destruction', on_delete=models.CASCADE, verbose_name='الفرع الهدف')
    transfer_date_destruction = models.DateField(default=timezone.now, verbose_name='تاريخ التحويل')
   
    

    def __str__(self):
        return f"{self.asset} - {self.source_branch_destruction} to {self.destination_branch_destruction}"
   

class UserBranchPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'branch')

class UserPermission(models.Model):
    CHOICE_FIELD = [
        ("screenViewInvoices", 'شاشة الفواتير'),
        ("screenViewDestruction",'شاشة الاهلاك'),
        ("screenViewTransfer",'شاشة التحويل'),
        ("screenViewGroup",'شاشة التصنيف'),
        ("screenViewPranches",'شاشة الفروع'),
        ("screenViewAdditionTax",'شاشة اضافة ضريبة الزيادة'),
        ("screenViewMinusTax",'شاشة اضافة ضريبة الخصم'),
        ("screenViewCoast",'شاشة اضافة المصروف'),
        ("screenViewPermission",'شاشة اضافة لصلاحيات'),
       
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
   
    permission =  models.CharField(max_length=255, choices=CHOICE_FIELD, verbose_name='صلاحية الشاشات', default='screenViewInvoices')
    def __str__(self):
        return f"{self.permission}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allowed_branches = models.ManyToManyField(Branch)  # الفروع التي يمكن للمستخدم رؤيتها





