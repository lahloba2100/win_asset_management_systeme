from django.urls import path

from add_asset_invoice.decorators import HasPermission
from . import views, reports
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
  
    path('invoice-list/', HasPermission('screenViewInvoices')(views.AssetInvoiceList.as_view()), name='invoice-list'),
    path('permission-denied/', views.permission_denied, name='permission-denied'),
    path('index/', views.index, name='index'),
    #path('invoice-list', views.AssetInvoiceList.as_view(), name='invoice-list'),
    #path('invoice-list/', views.AssetInvoiceList.as_view(), name='invoice-list'),
    #path('invoice-list', views.AssetInvoiceList, name='invoice-list'),
   
    path('invoice/add/', views.AssetItemsCreate.as_view(), name='invoice-add'),
    path('update_invoice/<int:pk>', views.AssetItemsUpdate.as_view(), name='invoice-update'),
    path('delete_invoice/<int:pk>', views.AssetInvoiceDelete.as_view(), name='invoice-delete'),
    
    path('group-list/', HasPermission('screenViewGroup')(views.AssetGroupList.as_view()), name='group-list'),
    #path('group-list', views.AssetGroupList.as_view(), name='group-list'),
    path('asset_group/add', views.AssetGroupCreate.as_view(), name='asset_group'),
    path('asset_group_update/<int:pk>', views.AssetGroupUpdate.as_view(), name='asset_group_update'),
    path('asset_group_delete/<int:pk>', views.AssetGroupDelete.as_view(), name='asset_group_delete'),
    
    
    path('branch-list/', HasPermission('screenViewPranches')(views.BranchList.as_view()), name='branch-list'),
    #path('branch-list', views.BranchList.as_view(), name='branch-list'),
    path('branch/add', views.BranchCreate.as_view(), name='branch'),
    path('branch_update/<int:pk>', views.BranchUpdate.as_view(), name='branch_update'),
    path('branch_delete/<int:pk>', views.BranchDelete.as_view(), name='branch_delete'),
    
    path('systemadditiontax-list/', HasPermission('screenViewAdditionTax')(views.SystemAdditionTaxList.as_view()), name='systemadditiontax-list'),
    #path('systemadditiontax-list', views.SystemAdditionTaxList.as_view(), name='systemadditiontax-list'),
    path('systemaddition_tax/add', views.SystemAdditionTaxCreate.as_view(), name='systemaddition_tax'),
    path('systemaddition_tax_update/<int:pk>', views.SystemAdditionTaxUpdate.as_view(), name='systemaddition_tax_update'),
    path('systemaddition_tax_delete/<int:pk>', views.SystemAdditionTaxDelete.as_view(), name='systemaddition_tax_delete'),
    
    path('systemminustax-list/', HasPermission('screenViewMinusTax')(views.SystemMinusTaxList.as_view()), name='systemminustax-list'),
    #path('systemminustax-list', views.SystemMinusTaxList.as_view(), name='systemminustax-list'),
    path('systemminus_tax/add', views.SystemMinusTaxCreate.as_view(), name='systemminus_tax'),
    path('systemminus_tax_update/<int:pk>', views.SystemMinusTaxUpdate.as_view(), name='systemminus_tax_update'),
    path('systemminus_tax_delete/<int:pk>', views.SystemMinusTaxDelete.as_view(), name='systemminus_tax_delete'),
    
    path('systemexpensescost-list/', HasPermission('screenViewCoast')(views.SystemExpensesCostList.as_view()), name='systemexpensescost-list'),
    #path('systemexpensescost-list', views.SystemExpensesCostList.as_view(), name='systemexpensescost-list'),
    path('systemexpenses_cost/add', views.SystemExpensesCostCreate.as_view(), name='systemexpenses_cost'),
    path('systemexpenses_cost/<int:pk>', views.SystemExpensesCostUpdate.as_view(), name='systemexpenses_cost_update'),
    path('systemexpenses_cost/<int:pk>', views.SystemExpensesCostDelete.as_view(), name='systemexpenses_cost_delete'),
    
    path('destruction_list/', HasPermission('screenViewDestruction')(views.DestructionList.as_view()), name='destruction-list'),
    #path('destruction_list',  views.DestructionList.as_view(), name='destruction-list'),
    path('destruction_create',  views.DestructionCreate.as_view(), name='destruction-create'),
    path('destruction_update/<int:pk>', views.DestructionUpdate.as_view(), name='destruction-update'),
    
    path('asset_transfers/', HasPermission('screenViewTransfer')(views.TransferListView.as_view()), name='asset_transfers'),
    #path('asset_transfers', views.TransferListView.as_view(), name='asset_transfers'),
    path('asset_transfer/create', views.TransferCreateView.as_view(), name='create_asset_transfer'),
    path('asset_transfer/update<int:pk>', views.TransferUpdateView.as_view(), name='update_asset_transfer'),
    path('asset_transfer_delete/<int:pk>', views.TransferDeleteView.as_view(), name='asset-transfer-delete'),
    path('get_asset_destruction/<int:asset_item>/', views.get_asset_destruction, name='get_asset_destruction'),
    path('get_asset_branch/<int:asset_id>/', views.get_asset_branch, name='get_asset_branch'),
    path('get_asset_branchupdate/<int:asset_id>/<int:transfer_id>/', views.get_asset_branchupdate, name='get_asset_branchupdate'),
    
    #path('generate_assets_report/', views.generate_assets_report_view, name='generate_assets_report'),
    #path('generate_assets_report/', views.generate_assets_report, name='generate_assets_report'),
    #path('generate_assets_report/<int:invoice_number_id>', views.generate_assets_report, name='generate_assets_report'),
    #path('generate_assets_report/<int:invoice_number_id>/', views.generate_assets_report, name='generate_assets_report'),
    path('generate_assets_report/<int:invoice_number_id>/', reports.AssetsReportView.as_view(), name='generate_assets_report'),
    path('generate_destruction_report/<int:asset_item_id>/', reports.DestructionReportView.as_view(), name='generate_destruction_report'),
    path('generate_tranfer_report/<int:transfer_destruction_id>/', reports.TranferReportView.as_view(), name='generate_tranfer_report'), 
    path('asset_report/', reports.asset_report, name='asset_report'),
    path('generate_reports_assets_report/', reports.ReportsAssetReportView.as_view(), name='generate_reports_assets_report'),
    
    path('destruction_report/', reports.destruction_report, name='destruction_report'),
    path('generate_reports_destruction_report/', reports.ReportsDestructionReportView.as_view(), name='generate_reports_destruction_report'), 
    
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # path('grant_permissions/', views.grant_branch_permissions, name='grant-branch-permissions'),
    #path('grant_permissions/', views.GrantBranchPermissionsView.as_view(), name='grant-branch-permissions'),
    #path('grant_permissions/', HasPermission('screenViewPermission')(views.grant_branch_permissions), name='grant-branch-permissions'),
    
    path('igrant_permissions_screen/', HasPermission('screenViewPermission')(views.GrantScreenPermissionsView.as_view()), name='grant-permissions-screen'),
    path('igrant_permissions/', HasPermission('screenViewPermission')(views.GrantBranchPermissionsView.as_view()), name='grant-branch-permissions'),
]


