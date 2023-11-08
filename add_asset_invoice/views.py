from functools import wraps
from django.forms import ValidationError
from django.shortcuts import redirect
from .models import *
from .forms import AssetItemsForm, PermissionChoiceForm, TransferForm, UserBranchPermissionShowForm, UserPermissionScreenForm
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .forms import AssetItemsFormSet, AdditionTaxFormSet, DestructionFormSet, ExpensesCostFormSet
from .forms import MinusTaxFormSet, TransferAssetFormSet,TransferDestructionDetailsFormSet
from .models import AssetInvoice
from .models import AssetItems, Destruction
import logging
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from .models import AssetInvoice
from django.contrib import messages
from django.shortcuts import render
from .forms import AssetReportForm
from .models import AssetItems
from datetime import datetime
from django.contrib.auth.password_validation import validate_password
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from .models import AssetInvoice
from .forms import AssetItemsFormSet, AdditionTaxFormSet, MinusTaxFormSet, ExpensesCostFormSet
from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import UserBranchPermissionForm
from django.shortcuts import render, redirect
from .forms import UserBranchPermissionForm
from .models import UserBranchPermission  # استيراد النموذج الذي قمنا بتعريفه في الخطوة 1
from .forms import UserPermissionViewScreenForm
from functools import wraps
from django.http import HttpResponseForbidden



@method_decorator(login_required, name='dispatch')
class AssetInvoiceList(ListView):
    model = AssetInvoice
    template_name = 'add_asset_invoice/assetinvoice_list.html'

    def get_context_data(self, **kwargs):
       
        context = super().get_context_data(**kwargs)
        has_permission_invoices = self.request.user.userpermission_set.filter(permission="screenViewInvoices").exists()
        context['has_permission_invoices'] = has_permission_invoices
        
        # قم بالتحقق من صلاحيات المستخدم للوصول إلى الفروع
        user = self.request.user
        user_permissions = UserBranchPermission.objects.filter(user=user)
        user_branches = user_permissions.values_list('branch_id', flat=True)
        
        # عرض الفروع المتاحة للمستخدم
        context['branches'] = Branch.objects.filter(id__in=user_branches)
        
        # استعلم عن الفرع المحدد إذا تم اختياره وقم بتصفية الفواتير بناءً على الفرع
        selected_branch = self.request.GET.get('branch')
        if selected_branch:
            selected_branch = int(selected_branch)
            if selected_branch in user_branches:
                context['selected_branch'] = selected_branch
                context['invoices'] = AssetInvoice.objects.filter(branch_name_id=selected_branch)
            else:
                # إذا كان المستخدم يحاول الوصول إلى فرع غير مصرح له، قم بتوجيهه إلى صفحة خطأ
                return redirect('error-page')  # قم بتغيير 'error-page' إلى عنوان الصفحة التي تحتاج إلى توجيه المستخدم إليها
        else:
            context['selected_branch'] = None
            context['invoices'] = AssetInvoice.objects.filter(branch_name_id__in=user_branches)

        return context

class AdditionTaxList(ListView):
    model = AdditionTax
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@method_decorator(login_required, name='dispatch')
class AssetItemsCreate(CreateView):
    model = AssetInvoice
    fields = ['invoice_number', 'invoice_date', 'company_name', 'supplier_phone', 'supplier_address', 
              'total_price','total_addition_tax','total_minus_tax', 'total_expences_cost','total_invoice_cost', 'amount_paid', 'remaining_balance', 
              'branch_name','invoice_image','invoice_pdf','supplier_name','id_card_number','commercial_record',
              'tax_card','bank_account_number_to','bank_name_to','bank_account_number_from','bank_name_from']
    success_url = reverse_lazy('invoice-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_id = self.request.user.id

        # تصفية حقل branch_name وعرض الفروع التي يتمتع بها المستخدم
        form.fields['branch_name'].queryset = Branch.objects.filter(userbranchpermission__user_id=user_id)

        return form
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user_id = self.request.user
        #user_branches = UserBranchPermission.objects.filter(user=user).values_list('branch', flat=True)
        #branches = Branch.objects.filter(id__in=user_branches)
        #user_id = self.request.session.get('user_id')
        user = user_id  # تمرير معرف المستخدم هنا
        data['user'] = AssetItemsForm(user=user)  # تمرير معرف المستخدم هنا
        print('useruser',user)

        if self.request.POST:
            #data['asset_items'] = AssetItemsFormSet(self.request.POST, user=self.request.user.id)
            #data['asset_items'] = AssetItemsFormSet(self.request.POST, user=user)  
            data['asset_items'] = AssetItemsFormSet(self.request.POST, form_kwargs={'user': user})  
            data['addition_tax'] = AdditionTaxFormSet(self.request.POST)
            data['minus_tax'] = MinusTaxFormSet(self.request.POST)
            data['expenses_cost'] = ExpensesCostFormSet(self.request.POST)
        else:
            #data['asset_items'] = AssetItemsFormSet(user=self.request.user.id)
            #data['asset_items'] = AssetItemsFormSet(user=user)
            data['asset_items'] = AssetItemsFormSet(form_kwargs={'user': user})
            data['addition_tax'] = AdditionTaxFormSet()
            data['minus_tax'] = MinusTaxFormSet()
            data['expenses_cost'] = ExpensesCostFormSet()
        
       

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        asset_items = context['asset_items']
        addition_tax = context['addition_tax']
        minus_tax = context['minus_tax']
        expenses_cost = context['expenses_cost']
        
        with transaction.atomic():
            self.object = form.save()

            if addition_tax.is_valid():
                addition_tax.instance = self.object
                addition_tax.save()
            else:
                print('addition_tax', addition_tax.errors)
                
            if minus_tax.is_valid():
                minus_tax.instance = self.object
                minus_tax.save()
                
            if expenses_cost.is_valid():
                expenses_cost.instance = self.object
                expenses_cost.save()

            if asset_items.is_valid():
                asset_items.instance = self.object
                asset_items.save()
            else:
                print('asset_items', asset_items.errors)
            
        return super().form_valid(form)

class AssetItemsUpdate(UpdateView):
    
    model = AssetInvoice
   
    fields = ['invoice_number', 'invoice_date', 'company_name', 'supplier_phone', 'supplier_address', 
              'total_price','total_addition_tax','total_minus_tax', 'total_expences_cost','total_invoice_cost', 'amount_paid', 'remaining_balance', 
              'branch_name','invoice_image','invoice_pdf','supplier_name','id_card_number','commercial_record',
              'tax_card','bank_account_number_to','bank_name_to','bank_account_number_from','bank_name_from']
    success_url = reverse_lazy('invoice-list')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_id = self.request.user.id

        # تصفية حقل branch_name وعرض الفروع التي يتمتع بها المستخدم
        form.fields['branch_name'].queryset = Branch.objects.filter(userbranchpermission__user_id=user_id)

        return form
    def get_context_data(self, **kwargs):
        data = super(AssetItemsUpdate, self).get_context_data(**kwargs)
        user_id = self.request.user
        user = user_id  # تمرير معرف المستخدم هنا
        data['user'] = AssetItemsForm(user=user)  # تمرير معرف المستخدم هنا
        print('useruser',user)
        if self.request.POST:
            #data['asset_items'] = AssetItemsFormSet(self.request.POST, instance=self.object)
            data['asset_items'] = AssetItemsFormSet(self.request.POST, instance=self.object, form_kwargs={'user': user})  
            data['addition_tax'] = AdditionTaxFormSet(self.request.POST, instance=self.object)
            data['minus_tax'] = MinusTaxFormSet(self.request.POST, instance=self.object)
            data['expenses_cost'] = ExpensesCostFormSet(self.request.POST, instance=self.object)
        else:
            #data['asset_items'] = AssetItemsFormSet(instance=self.object)
            data['asset_items'] = AssetItemsFormSet(instance=self.object, form_kwargs={'user': user})
            data['addition_tax'] = AdditionTaxFormSet(instance=self.object)
            data['minus_tax'] = MinusTaxFormSet(instance=self.object)
            data['expenses_cost'] = ExpensesCostFormSet(instance=self.object)
        # retrieve the object from the database
        asset_invoice = AssetInvoice.objects.get(pk=self.kwargs['pk'])
        
        # extract the image name
        image_name = asset_invoice.invoice_image.name if asset_invoice.invoice_image else ''
        #print("imagenameeeeeeeeeee", image_name)
        # add the image name to the context data
        data['image_name'] = image_name
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        asset_items = context['asset_items']
        addition_tax = context['addition_tax']
        minus_tax = context['minus_tax']
        expenses_cost = context['expenses_cost']
        
        'remove image from path'
        asset_invoice = AssetInvoice.objects.get(pk=self.kwargs['pk'])
        new_image_path = 'D:/project_django/asset_management_system/media/' + self.object.invoice_image.name if self.object.invoice_pdf else ''
         
        path_image_from_database = asset_invoice.invoice_image.name if asset_invoice.invoice_image else ''
        path_image_pk = 'D:/project_django/asset_management_system/media/' + path_image_from_database
        
        
        
        new_pdf_path = 'D:/project_django/asset_management_system/media/' + self.object.invoice_pdf.name if self.object.invoice_pdf else ''
       
        path_pdf_from_database = asset_invoice.invoice_pdf.name if asset_invoice.invoice_pdf else ''
        path_pdf_pk = 'D:/project_django/asset_management_system/media/' + path_pdf_from_database
        print('old and new pdf', path_pdf_pk, new_pdf_path)
        if os.path.exists(path_image_pk) and path_image_from_database and path_image_pk != new_image_path:
            os.remove(path_image_pk)
        elif os.path.exists(path_image_pk) and path_image_from_database and path_image_pk == new_image_path:
            print("file image exist")
            
        else:
            print("file image not exist")
            
        # بعد التعديل
        if os.path.exists(path_pdf_pk) and path_pdf_from_database and path_pdf_pk != new_pdf_path:
            os.remove(path_pdf_pk)
        elif os.path.exists(path_pdf_pk) and path_pdf_from_database and path_pdf_pk == new_pdf_path:
            print("file pdf exist")
        else:
            print("file pdf not exist")


            
        with transaction.atomic():
            self.object = form.save(commit=False)
            if self.request.FILES:
                image_file = self.request.FILES.get('invoice_image')
                if image_file:
                    # delete old image if exists
                    if self.object.invoice_image:
                        # get the old image name
                        old_image_name = self.object.invoice_image.name
                        # generate a new unique name for the image
                        new_image_name = default_storage.get_available_name(image_file.name)
                        # delete old image
                        default_storage.delete(old_image_name)
                       
                        # save new image
                        self.object.invoice_image.save(new_image_name, ContentFile(image_file.read()))
                    else:
                        self.object.invoice_image.save(image_file.name, ContentFile(image_file.read()))
                        
            self.object.save()
            if addition_tax.is_valid():
                addition_tax.instance = self.object
                addition_tax.save()
            else:
                print("error say addition_tax.is not_valid", addition_tax.errors)
                
            if minus_tax.is_valid():
                minus_tax.instance = self.object
                minus_tax.save()
            else:
                print("error say minus_tax.is not_valid", minus_tax.errors)
                
            
            if expenses_cost.is_valid():
                expenses_cost.instance = self.object
                expenses_cost.save()
            else:
                print("error say expenses_cost.is not_valid", expenses_cost.errors)
           
            if asset_items.is_valid():
                asset_items.instance = self.object
                asset_items.save()
            else:
                print("error say asset_items.is not_valid", asset_items.errors)
            
        return super().form_valid(form)

class AssetItemsApproval(UpdateView):
   
    template_name_suffix = '_approval'
    model = AssetInvoice
    fields = ['invoice_number', 'invoice_date', 'supplier_name', 'supplier_phone', 'supplier_address', 
              'total_price','total_addition_tax','total_minus_tax', 'total_expences_cost','total_invoice_cost', 'amount_paid', 'remaining_balance', 
              'invoice_image','invoice_pdf']
    def get_success_url(self):
        return reverse_lazy('invoice-list')
    #success_url = reverse_lazy('invoice-list')
    
    def get_context_data(self, **kwargs):
        data = super(AssetItemsApproval, self).get_context_data(**kwargs)
        if self.request.POST:
            data['asset_items'] = AssetItemsFormSet(self.request.POST, instance=self.object)
            
        else:
            data['asset_items'] = AssetItemsFormSet(instance=self.object)
           
        
        return data
    
    def form_valid(self, form):
        context = self.get_context_data()
        asset_items = context['asset_items']
       
        asset_invoice = AssetInvoice.objects.get(pk=self.kwargs['pk'])
       
        with transaction.atomic():
            self.object = form.save(commit=False)
                
            if asset_items.is_valid():
                asset_items.instance = self.object
                asset_items.save()
            
            #return super(AssetItemsUpdate, self).form_valid(form)
            
        return super().form_valid(form)

class AssetInvoiceDelete(DeleteView):
    model = AssetInvoice
    success_url = reverse_lazy('invoice-list')

@method_decorator(login_required, name='dispatch')  
class AssetGroupList(ListView):
    model = AssetGroup
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_permission_group = self.request.user.userpermission_set.filter(permission="screenViewGroup").exists()
        context['has_permission_group'] = has_permission_group
        print('has_permission_grouphas_permission_group',has_permission_group)
        return context
        
class AssetGroupCreate(CreateView):
    model = AssetGroup
    fields = ['asset_group']
    success_url = reverse_lazy('group-list')

    def get_context_data(self, **kwargs):
        #, self.request.FILES['invoice_image']
        data = super(AssetGroupCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['asset_group'] = AssetItemsFormSet(self.request.POST)
        else:
            data['asset_group'] = AssetItemsFormSet()
        print('create dataaaaaaa', data)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        asset_group = context['asset_group']
        with transaction.atomic():
            self.object = form.save()

            if asset_group.is_valid():
                asset_group.instance = self.object
                asset_group.save()
        return super(AssetGroupCreate, self).form_valid(form)
    
class AssetGroupUpdate(UpdateView):
    model = AssetGroup
    #success_url = '/g'
    fields = ['asset_group']
    success_url = reverse_lazy('group-list')
    
class AssetGroupDelete(DeleteView):
    model = AssetGroup
    
    success_url = reverse_lazy('group-list')
    
@method_decorator(login_required, name='dispatch')
class BranchList(ListView):
    model = Branch
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_permission_branches = self.request.user.userpermission_set.filter(permission="screenViewPranches").exists()
        context['has_permission_branches'] = has_permission_branches
        return context
   
class BranchCreate(CreateView):
    model = Branch
    fields = ['branch_name']
    success_url = reverse_lazy('branch-list')

    def get_context_data(self, **kwargs):
        #, self.request.FILES['invoice_image']
        data = super(BranchCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['branch'] = AssetItemsFormSet(self.request.POST)
        else:
            data['branch'] = AssetItemsFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        branch = context['branch']
        with transaction.atomic():
            self.object = form.save()

            if branch.is_valid():
                branch.instance = self.object
                branch.save()
        return super(BranchCreate, self).form_valid(form)
  
class BranchUpdate(UpdateView):
    model = Branch
    #success_url = '/g'
    fields = ['branch_name']
    success_url = reverse_lazy('branch-list')
   
class BranchDelete(DeleteView):
    model = Branch
    
    success_url = reverse_lazy('branch-list') 
   
@method_decorator(login_required, name='dispatch')  
class SystemAdditionTaxList(ListView):
    model = SystemAdditionTax
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_permission_addition_tax = self.request.user.userpermission_set.filter(permission="screenViewAdditionTax").exists()
        context['has_permission_addition_tax'] = has_permission_addition_tax
        return context
   
class SystemAdditionTaxCreate(CreateView):
    model = SystemAdditionTax
    fields = ['addition_tax','addition_type','choice_field_coast','percent_addition_tax', 'value_addition_tax']
    success_url = reverse_lazy('systemadditiontax-list')

    def get_context_data(self, **kwargs):
        #, self.request.FILES['invoice_image']
        data = super(SystemAdditionTaxCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['systemaddition_tax'] = AssetItemsFormSet(self.request.POST)
        else:
            data['systemaddition_tax'] = AssetItemsFormSet()
        # print('create dataaaaaaa', data)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        systemaddition_tax = context['systemaddition_tax']
        with transaction.atomic():
            self.object = form.save()

            if systemaddition_tax.is_valid():
                systemaddition_tax.instance = self.object
                systemaddition_tax.save()
        return super(SystemAdditionTaxCreate, self).form_valid(form)

class SystemAdditionTaxUpdate(UpdateView):
    model = SystemAdditionTax
    #success_url = '/g'
    
    fields = ['addition_tax','addition_type','choice_field_coast','percent_addition_tax', 'value_addition_tax']
    success_url = reverse_lazy('systemadditiontax-list')

class SystemAdditionTaxDelete(DeleteView):
    model = SystemAdditionTax
    
    success_url = reverse_lazy('additiontax-list')

@method_decorator(login_required, name='dispatch')  
class SystemMinusTaxList(ListView):
    model = SystemMinusTax
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_permission_minus_tax = self.request.user.userpermission_set.filter(permission="screenViewMinusTax").exists()
        context['has_permission_minus_tax'] = has_permission_minus_tax
        return context
    
class SystemMinusTaxCreate(CreateView):
    model = SystemMinusTax
    fields = ['minus_tax','minus_type','choice_field_coast','percent_minus_tax', 'value_minus_tax']
    success_url = reverse_lazy('systemminustax-list')

    def get_context_data(self, **kwargs):
        #, self.request.FILES['invoice_image']
        data = super(SystemMinusTaxCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['minus_tax'] = AssetItemsFormSet(self.request.POST)
        else:
            data['minus_tax'] = AssetItemsFormSet()
        # print('create dataaaaaaa', data)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        minus_tax = context['minus_tax']
        with transaction.atomic():
            self.object = form.save()

            if minus_tax.is_valid():
                minus_tax.instance = self.object
                minus_tax.save()
        return super(SystemMinusTaxCreate, self).form_valid(form)

class SystemMinusTaxUpdate(UpdateView):
    model = SystemMinusTax
    #success_url = '/g'
    fields = ['minus_tax','minus_type','choice_field_coast','percent_minus_tax', 'value_minus_tax']
    success_url = reverse_lazy('minustax-list')

class SystemMinusTaxDelete(DeleteView):
    model = SystemMinusTax
    
    success_url = reverse_lazy('systemminustax-list')

@method_decorator(login_required, name='dispatch') 
class SystemExpensesCostList(ListView):
    model = SystemExpensesCost
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_permission_coast = self.request.user.userpermission_set.filter(permission="screenViewCoast").exists()
        context['has_permission_coast'] = has_permission_coast
        return context
    
class SystemExpensesCostCreate(CreateView):
    model = SystemExpensesCost
    fields = ['system_expenses_cost']
    success_url = reverse_lazy('systemexpensescost-list')

    def get_context_data(self, **kwargs):
        #, self.request.FILES['invoice_image']
        data = super(SystemExpensesCostCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['systemexpenses_cost'] = ExpensesCostFormSet(self.request.POST)
        else:
            data['systemexpenses_cost'] = ExpensesCostFormSet()
        # print('create dataaaaaaa', data)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        systemexpenses_cost = context['systemexpenses_cost']
        with transaction.atomic():
            self.object = form.save()

            if systemexpenses_cost.is_valid():
                systemexpenses_cost.instance = self.object
                systemexpenses_cost.save()
        return super(SystemExpensesCostCreate, self).form_valid(form)   
    
class SystemExpensesCostUpdate(UpdateView):
    model = SystemExpensesCost
    #success_url = '/g'
    fields = ['system_expenses_cost']
    success_url = reverse_lazy('systemexpenses_cost-list')

class SystemExpensesCostDelete(DeleteView):
    model = SystemExpensesCost
    
    success_url = reverse_lazy('systemexpenses_cost-list')

@method_decorator(login_required, name='dispatch') 
class DestructionList(ListView):
    model = AssetItems
    template_name = 'add_asset_invoice/destruction_list.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        has_permission_destruction = self.request.user.userpermission_set.filter(permission="screenViewDestruction").exists()
        context['has_permission_destruction'] = has_permission_destruction
        print('has_permission_destruction',has_permission_destruction)
        
        # قم بالتحقق من صلاحيات المستخدم للوصول إلى الفروع
        user = self.request.user
        user_permissions = UserBranchPermission.objects.filter(user=user)
        user_branches = user_permissions.values_list('branch_id', flat=True)
        
        # عرض الفروع المتاحة للمستخدم
        context['branches'] = Branch.objects.filter(id__in=user_branches)
        
        # استعلم عن الفرع المحدد إذا تم اختياره وقم بتصفية الفواتير بناءً على الفرع
        selected_branch = self.request.GET.get('branch')
        if selected_branch:
            selected_branch = int(selected_branch)
            if selected_branch in user_branches:
                context['selected_branch'] = selected_branch
                context['items'] = AssetItems.objects.filter(branch_name_id=selected_branch)
            else:
                # إذا كان المستخدم يحاول الوصول إلى فرع غير مصرح له، قم بتوجيهه إلى صفحة خطأ
                return redirect('error-page')  # قم بتغيير 'error-page' إلى عنوان الصفحة التي تحتاج إلى توجيه المستخدم إليها
        else:
            context['selected_branch'] = None
            context['items'] = AssetItems.objects.filter(branch_name_id__in=user_branches)

        return context
    
class DestructionCreate(CreateView):
    model = AssetItems
    template_name = 'add_asset_invoice/destruction_form.html'
    form_class = DestructionFormSet
    success_url = 'destruction-list'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset'] = DestructionFormSet(self.request.POST)
        else:
            data['formset'] = DestructionFormSet()
        return data

    def form_valid(self, form):
        formset = DestructionFormSet(self.request.POST)
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
        
class DestructionUpdate(UpdateView):
    model = AssetItems
    fields = ['invoice_number','asset_number', 'asset_name', 'asset_description','count', 'price', 'asset_price', 
              'destruction_percent','destruction_value','destruction_start_month', 'destruction_end_month', 'branch_name']
    template_name = 'add_asset_invoice/destruction_form.html'
    success_url = reverse_lazy('destruction-list')
    


    def get_context_data(self, **kwargs):
        
        data = super(DestructionUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['destruction'] = DestructionFormSet(self.request.POST, instance=self.object)
        else:
            data['destruction'] = DestructionFormSet(instance=self.object)
       
        return data

    def form_valid(self, form):
        
        context = self.get_context_data()
        destruction = context['destruction']
       
        with transaction.atomic():
            self.object = form.save()
            if destruction.is_valid():
            #if destruction.is_valid() and destruction.cleaned_data['destruction_value'] != "":

                destruction.instance = self.object
                destruction.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        logger.error('Form is invalid: %s', form.errors)
        return super().form_invalid(form)
    def handle_no_permission(self):
        logger.error('Permission denied')
        return super().handle_no_permission()
    
@method_decorator(login_required, name='dispatch')    
class TransferListView(ListView):
    model = Transfer
    template_name = 'add_asset_invoice/assettransfer_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_permission_transfer = self.request.user.userpermission_set.filter(permission="screenViewTransfer").exists()
        context['has_permission_transfer'] = has_permission_transfer
        return context
  
class TransferDeleteView(DeleteView):
    model = Transfer
    template_name = 'add_asset_invoice/assettransfer_confirm_delete.html'
    success_url = reverse_lazy('asset_transfers')

def get_asset_destruction(request, asset_item):
    destructions = Destruction.objects.filter(asset_item_id=asset_item).values('pk','destruction_start_month', 'branch_name__branch_name', 'destruction_value')
    return JsonResponse(list(destructions), safe=False)

def get_asset_branch(request, asset_id):
    branches = Branch.objects.filter(assetitems__id=asset_id).values('pk', 'branch_name')
    return JsonResponse(list(branches), safe=False)

def get_asset_branchupdate(request, asset_id, transfer_id):
    branches = Branch.objects.filter(source_transfers__asset=asset_id, source_transfers__id=transfer_id).values('pk', 'branch_name')
    
    return JsonResponse(list(branches), safe=False)

class TransferCreateView(CreateView):
    model = Transfer
    template_name = 'add_asset_invoice/assettransfer_form.html'
    form_class = TransferForm
    success_url = reverse_lazy('asset_transfers')

    
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['transfer_id'] =0
       
        if self.request.POST:
            data['Transferasset'] = TransferAssetFormSet(self.request.POST)
            data['TransferdestructionDetails'] = TransferDestructionDetailsFormSet(self.request.POST)
            
        else:
            data['Transferasset'] = TransferAssetFormSet()
            data['TransferdestructionDetails'] = TransferDestructionDetailsFormSet()
           
        return data
    def get_initial(self):
        initial = super().get_initial()
        # قم بتعيين القيمة المطلوبة لحقل source_branch هنا
        # يمكنك استخدام أي طريقة تحدد قيمة الفرع المصدر المطلوبة
        initial['source_branch'] = Branch.objects.first()  # على سبيل المثال افتراضيًا نختار أول فرع في القاعدة
        return initial
    def form_valid(self, form):
        
        context = self.get_context_data()
        Transferasset = context['Transferasset']
        TransferdestructionDetails = context['TransferdestructionDetails']

        self.object = form.save(commit=False)
        destination_branch = form.cleaned_data.get('destination_branch')
        self.object.branch_name = destination_branch
        self.object.save()

        if Transferasset.is_valid() and TransferdestructionDetails.is_valid():
            self.object.save()
            Transferasset.instance = self.object
            Transferasset.save()
            TransferdestructionDetails.instance = self.object
            TransferdestructionDetails.save()
            # Update the branch_name for related AssetItems and Destructions
            AssetItems.objects.filter(transfer__id=self.object.id).update(branch_name=destination_branch)
            #Destruction.objects.filter(asset_item__transfer__id=self.object.id).update(branch_name=destination_branch)
            for destruction_detail in TransferdestructionDetails:
                try:
                    destruction = destruction_detail.instance.destruction
                    destination_branch_destruction = destruction_detail.instance.destination_branch_destruction
                    destruction.branch_name = destination_branch_destruction
                    destruction.save()
                except TransferDestructionDetails.destruction.RelatedObjectDoesNotExist:
                    pass
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
   
class TransferUpdateView(UpdateView):
    model = Transfer
    template_name = 'add_asset_invoice/assettransferupdate_form.html'
    form_class = TransferForm
    success_url = reverse_lazy('asset_transfers')
   
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        
        data['transfer_id'] = self.object.pk
        # بقية الكود
        if self.request.POST:
            data['Transferasset'] = TransferAssetFormSet(self.request.POST, instance=self.object)
            data['TransferdestructionDetails'] = TransferDestructionDetailsFormSet(self.request.POST, instance=self.object)
          
        else:
            data['Transferasset'] = TransferAssetFormSet(instance=self.object)
            data['TransferdestructionDetails'] = TransferDestructionDetailsFormSet(instance=self.object)
 
        return data
   
        
    
    def form_valid(self, form):
        context = self.get_context_data()
        Transferasset = context['Transferasset']
        TransferdestructionDetails = context['TransferdestructionDetails']
        
        self.object = form.save(commit=False)
        
        destination_branch_asset = Transferasset[0].instance.destination_branch_asset
        self.object.branch_name = destination_branch_asset
        self.object.save()

        if Transferasset.is_valid():
            Transferasset.save()

        if TransferdestructionDetails.is_valid():
            TransferdestructionDetails.save()
                
        destination_branch_asset = Transferasset[0].instance.destination_branch_asset
                
        if AssetItems.objects.filter(transfer__id__gt=self.object.id).exists():
            return HttpResponseForbidden("تم الحفظ بدون تغيير الفرع المصدر في الأصول والاهتلاك لوجود عملية تحويل أحدث")
        else:
            AssetItems.objects.filter(transfer__id=self.object.id).update(branch_name=destination_branch_asset)
            
        if Destruction.objects.filter(asset_item__transfer__id__gt=self.object.id).exists():
            return HttpResponseForbidden("تم الحفظ بدون تغيير الفرع المصدر في الأصول والاهتلاك لوجود عملية تحويل أحدث")
        else:
            for destruction_detail in TransferdestructionDetails:
                try:
                    destruction = destruction_detail.instance.destruction
                    destination_branch_destruction = destruction_detail.instance.destination_branch_destruction
                    destruction.branch_name = destination_branch_destruction
                    destruction.save()
                except TransferDestructionDetails.destruction.RelatedObjectDoesNotExist:
                    pass

        return super().form_valid(form)

def asset_report(request):
    #form = AssetReportForm(request.GET)
    #assets = []
    initial_data = {'start_date': '2000-01-01'}
    initial_data = {'end_date': datetime.today().date()}
    form = AssetReportForm(request.GET or None, initial=initial_data)
    assets = []

    if form.is_valid():
        #start_date = form.cleaned_data['start_date']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        asset_group = form.cleaned_data['asset_group']
        branch = form.cleaned_data['branch']

        assets = AssetItems.objects.filter(
            invoice_number__invoice_date__range=(start_date, end_date),
            #asset_group=asset_group,
            branch_name=branch
        )

    return render(request, 'reports/report_asset.html', {'form': form, 'assets': assets})

class SignupView(View):
    def get(self, request):
        form = UserCreationForm()
        
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password1')
            try:
                validate_password(password, user=None)
            except ValidationError as e:
                form.add_error('password1', e)
                messages.success(request,e)
                return render(request, 'registration/signup.html', {'form': form})
            else:
                user = form.save(commit=False)
                user.save()
                login(request, user)
                messages.success(request, 'تم تسجيل المستخدم بنجاح.')
                return redirect('invoice-list')
        else:
            #return render(request, 'registration/signup.html', {'form': form})
            messages.success(request, ' لم يتم تسجيل المستخدم بنجاح.')
            messages.success(request, form.error_messages)
            return render(request, 'parts/messages.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # قم بتوجيه المستخدم إلى الصفحة التي ترغب فيها بعد تسجيل الدخول
            #return render(request, 'index.html')
        else:
            messages.error(request, 'خطأ في اسم المستخدم أو كلمة المرور.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # قم بتوجيه المستخدم إلى صفحة تسجيل الدخول بعد تسجيل الخروج




@method_decorator(login_required, name='dispatch')
class GrantScreenPermissionsView(View):
    def get(self, request):
        
        form_add_permission_screen = UserPermissionScreenForm()
        form_view_permission_screen = UserPermissionViewScreenForm()
        available_screen = []

        return render(request, 'permissions/grant_permissions.html', {
            'available_screen': available_screen,
            'form_add_permission_screen': form_add_permission_screen,
            'form_view_permission_screen': form_view_permission_screen,
        })
    
    def post(self, request):
        form_add_permission_screen = UserPermissionScreenForm(request.POST)
        form_view_permission_screen = UserPermissionViewScreenForm(request.POST)
        
        if form_view_permission_screen.is_valid():
            user = form_view_permission_screen.cleaned_data['user']
            available_screen = form_view_permission_screen.get_available_screen()
            print('available_screenavailable_screen', available_screen)
        else:
            form_view_permission_screen = UserPermissionViewScreenForm()
            available_screen = []
            
        if form_add_permission_screen.is_valid():
            user = form_add_permission_screen.cleaned_data['user']
            selected_branches = form_add_permission_screen.cleaned_data['permissions']
            # حذف الصلاحيات السابقة للمستخدم للفروع المحددة
            UserPermission.objects.filter(user=user).delete()
            # منح الصلاحيات الجديدة للمستخدم للفروع المحددة
            for permission in selected_branches:
                permission = UserPermission(user=user, permission=permission)
                permission.save()
            return redirect('grant-permissions-screen')

        if form_add_permission_screen.is_valid():
            form_add_permission_screen.save()
            return redirect('grant-permissions-screen')  # توجيه المستخدم إلى صفحة الملف الشخصي بعد الحفظ

        return render(request, 'permissions/grant_permissions.html', {
            'available_screen': available_screen,
            'form_add_permission_screen': form_add_permission_screen,
            'form_view_permission_screen': form_view_permission_screen,
        })
    

@method_decorator(login_required, name='dispatch')
class GrantBranchPermissionsView(View):
    def get(self, request):
        form_view_permission_pranches = UserBranchPermissionShowForm()
        form_add_permission_pranches = UserBranchPermissionForm()
        available_branches = []
        
        return render(request, 'permissions/grant_permissions.html', {
            'form_view_permission_pranches': form_view_permission_pranches,
            'available_branches': available_branches,
            'form_add_permission_pranches': form_add_permission_pranches,
        })

    def post(self, request):
        form_view_permission_pranches = UserBranchPermissionShowForm(request.POST)
        form_add_permission_pranches = UserBranchPermissionForm(request.POST)

        if form_view_permission_pranches.is_valid():
            user = form_view_permission_pranches.cleaned_data['user']
            available_branches = form_view_permission_pranches.get_available_branches()
        else:
            form_view_permission_pranches = UserBranchPermissionShowForm()
            available_branches = []
        

        if form_add_permission_pranches.is_valid():
            user = form_add_permission_pranches.cleaned_data['user']
            selected_branches = form_add_permission_pranches.cleaned_data['branches']

            # حذف الصلاحيات السابقة للمستخدم للفروع المحددة
            UserBranchPermission.objects.filter(user=user).delete()

            # منح الصلاحيات الجديدة للمستخدم للفروع المحددة
            for branch in selected_branches:
                permission = UserBranchPermission(user=user, branch=branch)
                permission.save()

            return redirect('grant-branch-permissions')

        

        return render(request, 'permissions/grant_permissions.html', {
            'form_view_permission_pranches': form_view_permission_pranches,
            'available_branches': available_branches,
            'form_add_permission_pranches': form_add_permission_pranches,
        })


def index(request):
    return render(request, 'index.html')

def permission_denied(request):
    return render(request, 'permissions/permission_denied.html')


class UserListView(View):
    def get(self, request):
        users = User.objects.all()
        return render(request, 'permissions/user_list.html', {'users': users})

class UserDeleteView(View):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'المستخدم غير موجود.')
            return redirect('user-list')
        return render(request, 'permissions/user_delete_confirm.html', {'user': user})

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, 'تم حذف المستخدم بنجاح.')
        except User.DoesNotExist:
            messages.error(request, 'المستخدم غير موجود.')
        return redirect('user-list')
from .forms import CustomPasswordChangeForm
class ChangePasswordView(View):
    def get(self, request):
        form = CustomPasswordChangeForm(request.user)
        return render(request, 'permissions/change_password.html', {'form': form})

    def post(self, request):
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # تحديث جلسة المستخدم لتجنب تسجيل الخروج
            messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
            return redirect('change-password')
        else:
            messages.error(request, 'تعذر تغيير كلمة المرور. الرجاء التحقق من البيانات المدخلة.')
        return render(request, 'permissions/change_password.html', {'form': form})
