from django.contrib import admin
from .models import AssetInvoice, AssetItems, AssetGroup, Branch, SystemAdditionTax
from .models import  SystemMinusTax, AdditionTax, SystemExpensesCost, MinusTax,Destruction
from .models import  Transfer,TransferDestructionDetails, TransferAsset, UserPermission

from .models import UserBranchPermission
# Register your models here.
admin.site.register(SystemAdditionTax)
admin.site.register(SystemMinusTax)
admin.site.register(SystemExpensesCost)

admin.site.register(AssetInvoice)
admin.site.register(AssetGroup)
admin.site.register(AssetItems)
admin.site.register(AdditionTax)
admin.site.register(MinusTax)
admin.site.register(Branch)
admin.site.register(Destruction)
admin.site.register(Transfer)
admin.site.register(TransferDestructionDetails)
admin.site.register(TransferAsset)
admin.site.register(UserPermission)



admin.site.register(UserBranchPermission)
