import os
from django.forms import BaseModelFormSet, ModelForm, inlineformset_factory
from django import forms
from .models import AssetInvoice, AssetItems, AssetGroup, TransferDestructionDetails, Branch, Destruction, UserBranchPermission
from .models import ExpensesCost, MinusTax, SystemAdditionTax, AdditionTax, SystemMinusTax, Transfer, TransferAsset
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm   
from django.contrib.auth.models import User
from django import forms
from .models import UserBranchPermission
from django import forms
from .models import UserBranchPermission
from django import forms
from .models import UserPermission


class SystemMinusTaxForm(forms.ModelForm):
    
    class Meta:
        model = SystemMinusTax
        fields = [ 'minus_tax', 'minus_type', 'choice_field_coast', 'percent_minus_tax', 'value_minus_tax']
        
class SystemAdditionTaxForm(forms.ModelForm):
    
    class Meta:
        model = SystemAdditionTax
        fields = [ 'addition_tax', 'addition_type', 'choice_field_coast', 'percent_addition_tax', 'value_addition_tax']

class AssetGroupForm(forms.ModelForm):
    
    class Meta:
        model = AssetGroup
        fields = [ 'asset_group']

class BranchForm(forms.ModelForm):
    
    class Meta:
        model = Branch
        fields = ['branch_name']
              
class AssetInvoiceForm(forms.ModelForm):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), label='اختر الفرع')
    class Meta:
        model = AssetInvoice
        fields = ['invoice_number', 'invoice_date', 'company_name', 'supplier_phone', 'supplier_address', 
              'total_price','total_addition_tax','total_minus_tax', 'total_expences_cost','total_invoice_cost', 'amount_paid',
               'remaining_balance', 'branch_name','invoice_image','invoice_pdf','supplier_name','id_card_number','commercial_record',
              'tax_card','bank_account_number_to','bank_name_to','bank_account_number_from','bank_name_from']
        
        widgets = {
           
            'invoice_number' :forms.TextInput(attrs={'class':'form-control'}),
            'invoice_date':forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
            'company_name':forms.TextInput(attrs={'class':'form-control'}),
            'supplier_phone':forms.TextInput(attrs={'class':'form-control'}),
            'supplier_address':forms.TextInput(attrs={'class':'form-control'}),
            
            'total_price':forms.TextInput(attrs={'class':'form-control'}),

            'total_addition_tax':forms.TextInput(attrs={'class':'form-control'}),
            'total_minus_tax':forms.TextInput(attrs={'class':'form-control'}),
            'total_expences_cost':forms.TextInput(attrs={'class':'form-control'}),


            'total_invoice_cost':forms.TextInput(attrs={'class':'form-control'}),
            'amount_paid':forms.TextInput(attrs={'class':'form-control'}),
            'remaining_balance':forms.TextInput(attrs={'class':'form-control'}),

            'remaining_balance':forms.TextInput(attrs={'class':'form-control'}),
            'branch_name':forms.TextInput(attrs={'class':'form-control'}),
            'invoice_image':forms.FileInput(attrs={'class':'form-control'}),
            'invoice_pdf':forms.TextInput(attrs={'class':'form-control'}),
            'supplier_name':forms.TextInput(attrs={'class':'form-control'}),
            'id_card_number':forms.TextInput(attrs={'class':'form-control'}),

            'commercial_record':forms.TextInput(attrs={'class':'form-control'}),
            'tax_card':forms.TextInput(attrs={'class':'form-control'}),
            'bank_account_number_to':forms.TextInput(attrs={'class':'form-control'}),
            'bank_name_to':forms.TextInput(attrs={'class':'form-control'}),

            'bank_account_number_from':forms.TextInput(attrs={'class':'form-control'}),
            'bank_name_from':forms.TextInput(attrs={'class':'form-control'}),
            
        }
    invoice_image = forms.FileField(required=False)
    def save(self, commit=True):
        invoice = super(AssetInvoiceForm, self).save(commit=False)
        if 'invoice_image' in self.files:
            image = self.files['invoice_image']
            invoice.invoice_image = self.handle_uploaded_file(image)
        if commit:
            invoice.save()
        return invoice
    
    def clean_invoice_pdf(self):
        invoice_pdf = self.cleaned_data.get('invoice_pdf')
        if invoice_pdf:
            if not invoice_pdf.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed')
            if invoice_pdf.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 5 MB')
        return invoice_pdf
    
    def handle_uploaded_file(self, f):
        file_path = os.path.join('media', 'invoice_images', f.name)
        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return file_path
        
'''class AssetItemsForm(forms.ModelForm):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False, label='اختر الفرع')
    class Meta:
        model = AssetItems
        fields = ['invoice_number', 'asset_number','asset_name', 'asset_group','asset_description','count', 'price', 'asset_price','branch_name']
        widgets = {
                'asset_number': forms.TextInput(attrs={}),
                'asset_description': forms.Textarea(attrs={'style': 'height: 2em;'}),
            }'''


'''class AssetItemsForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # قم بالتحقق من صلاحيات المستخدم للوصول إلى الفروع
        user_permissions = UserBranchPermission.objects.filter(user=user)
        user_branches = user_permissions.values_list('branch_id', flat=True)
        
        # استخدام قائمة الفروع لتحديث قائمة الفروع في النموذج
        self.fields['branch_name'].queryset = Branch.objects.filter(id__in=user_branches)

    class Meta:
        model = AssetItems
        fields = ['invoice_number', 'asset_number', 'asset_name', 'asset_group', 'asset_description', 'count', 'price', 'asset_price', 'branch_name']
        widgets = {
            'asset_number': forms.TextInput(attrs={}),
            'asset_description': forms.Textarea(attrs={'style': 'height: 2em;'}),
        }'''


'''class AssetItemsForm(forms.ModelForm):
    #branch_name = forms.ChoiceField(choices=(), label='اختر الفرع')
    #branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False, label='اختر الفرع')
    user_passed = False
    class Meta:
        model = AssetItems
        fields = ['invoice_number', 'asset_number', 'asset_name', 'asset_group', 'asset_description', 'count', 'price', 'asset_price', 'branch_name']
        widgets = {
            'asset_number': forms.TextInput(attrs={}),
            'asset_description': forms.Textarea(attrs={'style': 'height: 2em;'}),
        }
    
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user', None)  # استخراج معرف المستخدم من وسائط kwargs
        super(AssetItemsForm, self).__init__(*args, **kwargs)
        if user_id is not None and user_id.is_authenticated:  # التحقق من أن المستخدم موجود ومسجل دخول
            user_permissions = UserBranchPermission.objects.filter(user_id=user_id)
            user_branches = user_permissions.values_list('branch_id', flat=True)
            self.fields['branch_name'].queryset = Branch.objects.filter(id__in=user_branches)
            self.fields['branch_name'].empty_label = "اختر الفرع 1" 
        else:
            self.fields['branch_name'].queryset = Branch.objects.none()  # إرجاع قائمة فارغة من الفروع
            self.fields['branch_name'].empty_label = "لا يوجد فروع متاحة"  # يمكنك تغيير هذه القيمة حسب احتياجاتك'''

'''class AssetItemsForm(forms.ModelForm):
    #branch_name = forms.ChoiceField(choices=(), label='اختر الفرع')
    #branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False, label='اختر الفرع')
    user_passed = False
    class Meta:
        model = AssetItems
        fields = ['invoice_number', 'asset_number', 'asset_name', 'asset_group', 'asset_description', 'count', 'price', 'asset_price', 'branch_name']
        widgets = {
            'asset_number': forms.TextInput(attrs={}),
            'asset_description': forms.Textarea(attrs={'style': 'height: 2em;'}),
        }
    
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user', None)  # استخراج معرف المستخدم من وسائط kwargs
        super(AssetItemsForm, self).__init__(*args, **kwargs)
        print(' user_id is not None', user_id is not None)
        if user_id is not None:
            print(' user_id', user_id)
            user_permissions = UserBranchPermission.objects.filter(user_id=user_id)
            user_branches = user_permissions.values_list('branch_id', flat=True)
            print('user_branches', user_branches)
            self.fields['branch_name'].queryset = Branch.objects.filter(id__in=user_branches)
            self.fields['branch_name'].empty_label = "اختر الفرع 1" 
        else:
            print(' user_id', user_id)
            user_permissions = UserBranchPermission.objects.filter(user_id=0)  # أو أي قيمة تناسب الحالة الأخرى
            user_branches = user_permissions.values_list('branch_id', flat=True)
            print('user_branches', user_branches)
            self.fields['branch_name'].queryset = Branch.objects.filter(id__in=user_branches)
            self.fields['branch_name'].empty_label = "اختر الفرع 2"  # يمكنك تغيير هذه القيمة حسب احتياجاتك
'''

class AssetItemsForm(forms.ModelForm):
    #branch_name = forms.ChoiceField(choices=(), label='اختر الفرع')
    #branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=False, label='اختر الفرع')
    #user_passed = False
    class Meta:
        model = AssetItems
        fields = ['invoice_number', 'asset_number', 'asset_name', 'asset_group', 'asset_description', 'count', 'price', 'asset_price', 'branch_name']
        widgets = {
            'asset_number': forms.TextInput(attrs={}),
            'asset_description': forms.Textarea(attrs={'style': 'height: 2em;'}),
        }         
    def __init__(self, *args, **kwargs):
        
        #user = kwargs.pop('user', 1)  # استخراج معرف المستخدم من وسائط kwargs
        #user = 1
        user = kwargs.pop('user', None)  # استخراج معرف المستخدم من وسائط kwargs
        super(AssetItemsForm, self).__init__(*args, **kwargs)
       
        
        user_id = user
        print('useruseruseruser', user_id )
        if user:
            
            
            #print('useruseruseruser', user_id )
            user_permissions = UserBranchPermission.objects.filter(user_id=user_id)
            user_branches = user_permissions.values_list('branch_id', flat=True)
            self.fields['branch_name'].queryset = Branch.objects.filter(id__in=user_branches)
            self.fields['branch_name'].empty_label = "اختر 1111 الفرع" 
        else:
            #print('useruseruseruser', user_id )
            #print('self.user==1', self.user==1 )
            user_permissions = UserBranchPermission.objects.filter(user_id=user_id)
            user_branches = user_permissions.values_list('branch_id', flat=True)
            self.fields['branch_name'].queryset = Branch.objects.filter(id__in=user_branches)
            self.fields['branch_name'].empty_label = "اختر2222 الفرع"  # يمكنك تغيير هذه القيمة حسب احتياجاتك
                 
class AdditionTaxForm(forms.ModelForm):
    class Meta:
        model = AdditionTax
        fields = ['invoice_number', 'addition_tax','value_tax_increase']
        
class MinusTaxForm(forms.ModelForm):
    #asset_group = forms.ModelChoiceField(queryset=SystemAdditionTax.objects.all(), empty_label="Select an asset group")
    class Meta:
        model = MinusTax
        fields = ['invoice_number', 'minus_tax','value_tax_decrease']
        
class ExpensesCostForm(forms.ModelForm):
    #asset_group = forms.ModelChoiceField(queryset=SystemAdditionTax.objects.all(), empty_label="Select an asset group")
    class Meta:
        model = ExpensesCost
        fields = ['invoice_number', 'expenses_cost','value_expenses_cost']
        
class DestructionForm(forms.ModelForm):
    class Meta:
        model = Destruction
        fields = ['asset_item', 'destruction_start_month', 'destruction_end_month', 'destruction_percent', 'destruction_value','branch_name']
    
class TransferForm(forms.ModelForm):
    
    class Meta:
        model = Transfer
        fields = ['id', 'asset', 'source_branch', 'destination_branch', 'transfer_date', 'transfer_title']
        
        widgets = {
                'transfer_title': forms.Textarea(attrs={'id': 'id_transfer_title', 'style': 'height: 2em;'}),
            }
         
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.source_branch:
            asset_id = self.instance.asset_id if self.instance else None
            transfer_id = self.instance.pk if self.instance else None
            branches = Branch.objects.filter(source_transfers__asset=asset_id,source_transfers__id=transfer_id).values_list('pk', 'branch_name')
            self.fields['source_branch'].choices = [('', '----dd-----')]
            self.fields['source_branch'].choices += branches
            #print('fieldfield', branches, asset_id, transfer_id)
            
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance and not cleaned_data.get('source_branch'):
            raise forms.ValidationError('يجب تحديد الفرع المصدر')
        return cleaned_data
    
class TransferAssetForm(forms.ModelForm):
    class Meta:
        model = TransferAsset
        fields = ['id', 'transfer_asset', 'asset', 'source_branch_asset', 'destination_branch_asset', 'transfer_date_asset']
    
    def __init__(self, *args, **kwargs):
        super(TransferAssetForm, self).__init__(*args, **kwargs)
        #print('selfff.fieldsTransferasset', self.instance.asset_id, self.instance.transfer_asset_id)
        #asset_id = self.instance.asset_id
        #transfer_id = self.instance.transfer_asset_id
        asset_id = self.instance.asset_id if self.instance else None
        transfer_id = self.instance.transfer_asset_id if self.instance else None
            
        branches = Branch.objects.filter(source_transfers_asset__asset=asset_id,source_transfers__id=transfer_id).values_list('pk', 'branch_name')
        self.fields['source_branch_asset'].choices = [('', '----ddd-----')]
        self.fields['source_branch_asset'].choices += branches
        
        
        
        # تحديد queryset لحقل source_branch_asset بناءً على الأصل المحدد
        '''if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance.asset:
                self.fields['source_branch_asset'].queryset = instance.asset.branch_name.all()
            else:
                self.fields['source_branch_asset'].queryset = self.fields['source_branch_asset'].queryset.none()
            '''
        # تحديد queryset لحقل destination_branch_asset بناءً على الأصل المحدد
        '''if 'data' in kwargs:
            data = kwargs['data']
            asset_id = data.get('asset')
            if asset_id:
                self.fields['destination_branch_asset'].queryset = Branch.objects.filter(destination_transfers_asset__asset_id=asset_id)
            else:
                self.fields['destination_branch_asset'].queryset = self.fields['destination_branch_asset'].queryset.none()
                '''
    
class TransferDestructionDetailsForm(forms.ModelForm):
    class Meta:
        model = TransferDestructionDetails
        fields = ['transfer_destruction', 'asset', 'destruction', 'source_branch_destruction', 'destination_branch_destruction', 'transfer_date_destruction']
        #delete = forms.BooleanField(required=False)
            #'asset' :forms.Select(attrs={'class':'disabled'}),
            
            #'invoice_date':forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
            #'supplier_name':forms.TextInput(attrs={'class':'form-control'}),
            #'supplier_phone':forms.TextInput(attrs={'class':'form-control'}),
            #'supplier_address':forms.TextInput(attrs={'class':'form-control'}),
            
            #'total_price':forms.TextInput(attrs={'class':'form-control'}),
            #'total_invoice_cost':forms.TextInput(attrs={'class':'form-control'}),
            #'amount_paid':forms.TextInput(attrs={'class':'form-control'}),
            #'remaining_balance':forms.TextInput(attrs={'class':'form-control'}),
            #'invoice_image':forms.FileInput(attrs={'class':'form-control'}),
    
    def __init__(self, *args, **kwargs):
        super(TransferDestructionDetailsForm, self).__init__(*args, **kwargs)
        #print('selfff.fieldsTransferasset', self.instance.asset_id, self.instance.transfer_destruction_id)
        
        #asset_id = self.instance.asset_id
        #transfer_id = self.instance.transfer_destruction_id
        asset_id = self.instance.asset_id if self.instance else None
        transfer_id = self.instance.transfer_destruction_id if self.instance else None
        transfer_pk =  self.instance.pk if self.instance else None
        branchess = Branch.objects.filter(source_transfers_destruction__asset=asset_id,source_transfers_destruction__pk=transfer_pk).values_list('pk', 'branch_name')
        #print('qqqqqqqqq',Destruction._meta.get_fields())

        #branchess = Branch.objects.filter(source_transfers_destruction__asset=asset_id,source_transfers__id=transfer_id).values_list('pk', 'branch_name')
        self.fields['source_branch_destruction'].choices = [('', '----ddd-----')]
        self.fields['source_branch_destruction'].choices += branchess
        #print('self.instance.asset_idself.instance.asset_idself.instance.asset_id', self.instance.pk)
        
        ###destructions = Destruction.objects.filter(asset_item_id=asset_id).values_list('pk','destruction_start_month')
        destructions = Destruction.objects.filter(asset_item_id=asset_id).values_list('pk', 'destruction_start_month', 'branch_name__branch_name', 'destruction_value')

        # إفراغ قائمة الاختيار في نموذج TransferDestructionDetailsForm
        self.fields['destruction'].choices = [('', '----ddd-----')]
        self.fields['destruction'].choices += [(destruction[0], f'{destruction[1]} - {destruction[2]} - {destruction[3]}') for destruction in destructions]


        #destruction = Destruction.objects.filter(asset_item_id=asset_id).values_list('pk','destruction_value')
        #destructions = Destruction.objects.filter(asset_item_id=asset_id).values_list('pk','destruction_value')
        #destructions = Destruction.objects.filter(destination_transfers_key__asset=asset_id).values_list('pk', 'destruction_value')
        ##self.fields['destruction'].choices = [('', '----ddd-----')]
        ##self.fields['destruction'].choices += destructions
       
        
    
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance and not cleaned_data.get('source_branch_destruction'):
            raise forms.ValidationError('يجب تحديد الفرع المصدر')
        return cleaned_data
       
class AssetReportForm(forms.Form):
    start_date = forms.DateField(label='تاريخ الشراء من', initial='2000-01-01')
    end_date = forms.DateField(label='الي', initial=datetime.today)
    asset_group = forms.ModelChoiceField(queryset=AssetGroup.objects.all(), empty_label='اختر تصنيف الأصل',required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), empty_label='اختر الفرع')
    
class DestructionReportForm(forms.Form):
    #asset_group = forms.ModelChoiceField(queryset=AssetGroup.objects.all(), empty_label='اختر تصنيف الأصل',required=False)
    #branch = forms.ModelChoiceField(queryset=Branch.objects.all(), empty_label='اختر الفرع', initial=1)
    #start_date = forms.DateField(label='تاريخ الشراء من', initial='2000-01-01', widget=forms.DateInput(attrs={'id': 'startDate'}),)
    start_date = forms.DateField(label='تاريخ الشراء من', initial='2000-01-01')
    end_date = forms.DateField(label='الي', initial=datetime.today)
    asset_group_choices = [(asset_group.id, str(asset_group)) for asset_group in AssetGroup.objects.all()]
    asset_group = forms.ChoiceField(choices=[('', 'كل التصنيفات')] + asset_group_choices,required=False)
    branch_choices = [(branch.id, str(branch)) for branch in Branch.objects.all()]
    branch = forms.ChoiceField(choices=[('', 'اختر الفرع')] + branch_choices)
     # حقل الاختيار (RadioButton) للـ Option
    OPTION_CHOICES = [
        ('option1', 'تفصيلي'),
        ('option2', 'اجمالي'),
        
        # يمكنك إضافة المزيد من الخيارات هنا
    ]
    option = forms.ChoiceField(label='Option', initial='option2', choices=OPTION_CHOICES, widget=forms.RadioSelect(), required=False)

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2') 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تعيين الحد الأدنى لطول كلمة المرور إلى 8
        self.fields['password1'].min_length = 1

class LoginForm(forms.Form):
    username = forms.CharField(label='اسم المستخدم', max_length=100)
    password = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput)

class UserBranchSelectionForm(forms.Form):
    # الفروع المتاحة للمستخدم في قائمة الفواتير وقائمة الاهلاك
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='اختر المستخدم')
    branches = forms.ModelMultipleChoiceField(queryset=Branch.objects.all(), widget=forms.CheckboxSelectMultiple, label='الفروع')



class PermissionChoiceForm(forms.Form):
    CHOICES = (
        ('branches', 'صلاحية الفروع'),
        ('screens', 'صلاحية الشاشات'),
    )
    choice = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'choice-field'}),  # أضف الفئة الخاصة بك هنا
        label='',
        initial='branches'  # تعيين 'branches' كقيمة افتراضية
    )


class UserBranchPermissionForm(forms.Form):
    # اضافة صلاحية الفروع
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='')
    branches = forms.ModelMultipleChoiceField(queryset=Branch.objects.all(), widget=forms.CheckboxSelectMultiple, label='')
    
      
    def __init__(self, *args, **kwargs):
        super(UserBranchPermissionForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'selectpicker'  # تخصيص العرض إذا كنت تستخدم Bootstrap أو أي استايل آخر

    def get_available_branches(self):
        user = self.cleaned_data.get('user')
        if user:
            return UserBranchPermission.objects.filter(user=user).values_list('branch', flat=True)
        return []

class UserBranchPermissionShowForm(forms.Form):
    # عرض صلاحية الفروع
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="")
    #<ul class="errorlist"><li>This field is required.</li></ul>    
    branches = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label='')
    
    def __init__(self, *args, **kwargs):
        super(UserBranchPermissionShowForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'selectpicker'  # تخصيص العرض إذا كنت تستخدم Bootstrap أو أي استايل آخر

    def get_available_branches(self):
        user = self.cleaned_data.get('user')
        if user:
            user_permissions = UserBranchPermission.objects.filter(user=user)

            branches = Branch.objects.values('id', 'branch_name')
            branch_choice = []

            for branch in branches:
                branch_id = branch['id']
                branch_name = branch['branch_name']
                has_permission = any(permission.branch.id == branch_id for permission in user_permissions)

                branch_choice.append([branch_id, branch_name] if has_permission else ["", ""])

            branch_choices = branch_choice

            #branch_choices = [(str(permission.branch.id), permission.branch.branch_name) for permission in user_permissions]
            self.fields['branches'].choices = branch_choices
            selected_branches = UserBranchPermission.objects.filter(user=user).values_list('branch__id', flat=True)
            
            self.fields['branches'].initial = [str(branch_id) for branch_id in selected_branches]
        else:
            self.fields['branches'].choices = []

        # تحديد جميع الخيارات تلقائيًا
        self.fields['branches'].initial = [str(branch[0]) for branch in branch_choices]
        

class UserPermissionScreenForm(forms.Form):
    # اضافة صلاحية الفروع
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='')
    permissions = forms.MultipleChoiceField(choices=UserPermission.CHOICE_FIELD, widget=forms.CheckboxSelectMultiple, label='اختر الشاشة')

    def __init__(self, *args, **kwargs):
        super(UserPermissionScreenForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'selectpicker'  # تخصيص العرض إذا كنت تستخدم Bootstrap أو أي استايل آخر

    def get_available_permissions(self):
        user = self.cleaned_data.get('user')
        if user:
            return UserPermission.objects.filter(user=user).values_list('permission', flat=True)
        return []
        
class UserPermissionViewScreenForm(forms.Form):
    # عرض صلاحية الشاشات
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='')
    #permissions = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label='')
    permissions = forms.MultipleChoiceField( widget=forms.CheckboxSelectMultiple, required=False, label='عرض الصلاحيات')
    def __init__(self, *args, **kwargs):
        super(UserPermissionViewScreenForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = 'selectpicker'  # تخصيص العرض إذا كنت تستخدم Bootstrap أو أي استايل آخر
        
    def get_available_screen(self):
        user = self.cleaned_data.get('user')
        if user:
            # استعلام قاعدة البيانات للحصول على الصلاحيات المتاحة للمستخدم
            user_permissions = UserPermission.objects.filter(user=user).values_list('permission', flat=True)
            #choices = [(permission['permission'], permission['permission']) for permission in user_permissions]
            permissions=[]
            for permission in UserPermission.CHOICE_FIELD:
                if permission[0] in user_permissions:
                    print('permissionpermissionpermissionpermission', permission)
                    permissions.append(permission)
                else:
                     permissions.append(["",""])
            choices=(permissions)
                    
            #choices = [(permission) for permission in UserPermission.CHOICE_FIELD if permission[0] in user_permissions]
            #choices = [(permission, permission) for permission in UserPermission.CHOICE_FIELD if permission[0] in user_permissions]
            self.fields['permissions'].choices = choices
            selected_permissions = UserPermission.objects.filter(user=user).values_list('permission', flat=True)
            self.fields['permissions'].initial = [permission for permission in selected_permissions]
        else:
            self.fields['permissions'].choices = []
        # تحديد جميع الخيارات تلقائيًا
        #self.fields['permissions'].initial = [str(permission[0]) for permission in screen_choices]

    """def get_available_screen(self):
        user = self.cleaned_data.get('user')
        if user:
            user_permissions = UserPermission.objects.filter(user=user)
            return [permission.get_permission_display() for permission in user_permissions]  # استخدام get_FOO_display()

        return []"""



    
    
AssetItemsFormSet = inlineformset_factory(AssetInvoice, AssetItems,
                                            form=AssetItemsForm, extra=1)

AdditionTaxFormSet = inlineformset_factory(AssetInvoice, AdditionTax,
                                            form=AdditionTaxForm, extra=1)

MinusTaxFormSet = inlineformset_factory(AssetInvoice, MinusTax,
                                            form=MinusTaxForm, extra=1)

ExpensesCostFormSet = inlineformset_factory(AssetInvoice, ExpensesCost,
                                            form=ExpensesCostForm, extra=1)

DestructionFormSet = inlineformset_factory(AssetItems, Destruction, form=DestructionForm, extra=1)

TransferAssetFormSet = inlineformset_factory(Transfer, TransferAsset, form=TransferAssetForm, extra=1)
TransferDestructionDetailsFormSet = inlineformset_factory(Transfer, TransferDestructionDetails, form=TransferDestructionDetailsForm, extra=1)



