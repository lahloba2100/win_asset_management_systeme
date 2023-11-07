from collections import defaultdict
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.db.models import Q
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors

   
from django.views import View
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.shortcuts import get_object_or_404
from .models import *

from django.shortcuts import render
from .forms import AssetReportForm
from .models import AssetItems
from datetime import datetime
from .forms import DestructionReportForm
from django.shortcuts import render
from .forms import AssetReportForm
from .models import AssetItems
from datetime import datetime




def split_text(text, count):
    max_line_length = count
    words = text.split()  # تقسيم النص إلى كلمات
    
    # الآن سنقوم بتجميع الكلمات في جمل لا تتجاوز طول السطر المحدد
    chunks = []
    current_chunk = ""
    
    for word in words:
        if len(current_chunk) + len(word) <= max_line_length:
            current_chunk += " " + word
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    formatted_text = '\n'.join(chunks)
    return formatted_text

class AssetsReportView(View):
    
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.page_count = 0
        
    

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        invoice_number_id = kwargs.get('invoice_number_id')
        # استرجاع معلومات الفاتورة من جدول AssetInvoice
        invoice = get_object_or_404(AssetInvoice, pk=invoice_number_id)
        
        
        
        assets = AssetItems.objects.filter(invoice_number_id=invoice_number_id).values(
            'asset_number', 'asset_name', 'asset_group__asset_group', 'asset_description', 'price', 'count',
            'asset_price', 'destruction_value', 'branch_name__branch_name'
        )


        data = [
            ["الفرع", "قيمة الاهلاك", "القيمة", "العدد", "السعر", "البيان", "التصنيف", "اسم الأصل", "رقم الأصل"],
            *[
                [
                    split_text(asset['branch_name__branch_name'],10),
                    asset['destruction_value'],
                    asset['asset_price'],
                    asset['count'],
                    asset['price'],
                    split_text(asset['asset_description'], 44),
                    split_text(asset['asset_group__asset_group'],20),
                    split_text(asset['asset_name'],20),
                    asset['asset_number'],
                ]
                for asset in assets
            ]
        ]
        # ... (الواردة مسبقاً)
        addition_taxe = None
        if AdditionTax.objects.filter(invoice_number_id=invoice_number_id).exists():
            addition_taxe = get_object_or_404(AdditionTax, invoice_number_id=invoice_number_id)
            addition_taxes = AdditionTax.objects.filter(invoice_number_id=invoice_number_id).values(
                'addition_tax__addition_tax', 'value_tax_increase'
            )
            for addition_tax in addition_taxes:
                data.append([
                    "",
                    "",
                    addition_tax['value_tax_increase'],
                    "",
                    "",
                    addition_tax['addition_tax__addition_tax'],
                    "",
                    "",
                    "",
                ])
                
        minus_taxe = None
        if MinusTax.objects.filter(invoice_number_id=invoice_number_id).exists():
            minus_taxe = get_object_or_404(MinusTax, invoice_number_id=invoice_number_id)
            minus_taxes = MinusTax.objects.filter(invoice_number_id=invoice_number_id).values(
                'minus_tax__minus_tax', 'value_tax_decrease'
            )
            for minus_tax in minus_taxes:
                data.append([
                    "",
                    "",
                    minus_tax['value_tax_decrease'],
                    "",
                    "",
                    minus_tax['minus_tax__minus_tax'],
                    "",
                    "",
                    "",
                ])
        expenses_cost = None
        if ExpensesCost.objects.filter(invoice_number_id=invoice_number_id).exists():
            expenses_cost = get_object_or_404(ExpensesCost, invoice_number_id=invoice_number_id)
            expenses_costs = ExpensesCost.objects.filter(invoice_number_id=invoice_number_id).values(
                'expenses_cost__system_expenses_cost', 'value_expenses_cost'
            )
            for expenses_cost in expenses_costs:
                data.append([
                    "",
                    "",
                    expenses_cost['value_expenses_cost'],
                    "",
                    "",
                    expenses_cost['expenses_cost__system_expenses_cost'],
                    "",
                    "",
                    "",
                ])

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="assets_report_{invoice_number_id}.pdf"'

        buffer = BytesIO()
        #doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=100, bottomMargin=100)

        #arabic_font_path = "D:/project_django/asset_management_system/fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        #arabic_font_path = "H:/project_django/asset_management_system/fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))

        pdf = self.build_pdf(buffer, doc, invoice, addition_taxe, minus_taxe, expenses_cost, data)

        response.write(pdf)

        return response

    def build_pdf(self, buffer, doc, invoice, addition_taxe, minus_taxe, expenses_cost, data):
        reshaped_data = []
        for row in data:
            reshaped_row = [get_display(reshape(str(item))) for item in row]
            reshaped_data.append(reshaped_row)

        # عنوان التقرير
        title = [
            [get_display(reshape("تقرير الأصول المشتراة"))],
            [get_display(reshape(f"رقم الفاتورة: {invoice.invoice_number}"))],
            [get_display(reshape(f"تاريخ الفاتورة: {invoice.invoice_date}"))],
            [get_display(reshape(f"اسم المورد: {invoice.supplier_name}"))],
            [get_display(reshape(f"تليفون المورد: {invoice.supplier_phone}"))],
            [get_display(reshape(f"عنوان المورد: {invoice.supplier_address}"))],
        ]
        footer_text = [
            [get_display(reshape("ملخص الفاتورة "))],
            [get_display(reshape(f" الاجمالي: {invoice.total_invoice_cost}"))],
            [get_display(reshape(f" المدفوع: {invoice.amount_paid}"))],
            [get_display(reshape(f"المتبقي : {invoice.remaining_balance}"))],
            
        ]

        elements = []
        title_col_widths = [max(len(cell) for cell in row) for row in title]
        footer_col_widths = [max(len(cell) for cell in row) for row in footer_text]
        table_right_padding = -300

        title_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), table_right_padding),
        ])

        footer_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 300),
        ])

        # إعداد جداول العنوان والفوتر بالأنماط المحددة
        title_table = Table(title, colWidths=title_col_widths)
        title_table.setStyle(title_style)

        footer_table = Table(footer_text, colWidths=footer_col_widths)
        footer_table.setStyle(footer_style)

        # إعداد بيانات الجدول بالأنماط المحددة
         # إعداد بيانات الجدول بالأنماط المحددة
        col_widths = [60,40,65,35, 60, 214, 76, 77, 54]
        #data_table = Table(reshaped_data, colWidths=col_widths)
        
        data_table = Table(reshaped_data, colWidths=col_widths)
        data_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # توسيع النصوص الطويلة عمودياً
            #('COLWIDTHS', (0, 0), (-1, -1), col_widths)
            #('SPAN', (0, 0), (1, 0)),
        ])
        
        data_table.setStyle(data_style)

        # إعداد قالب لعرض العنوان والفوتر في الأعلى
        title_footer_template = Table([
            [title_table, footer_table]
        ], colWidths=[doc.width/2, doc.width/2])

        # إعداد الأنماط للتيتل والفوتر في القالب
        template_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), -40),
        ])
        
        title_footer_template.setStyle(template_style)

        
        elements = [title_footer_template, data_table]
        
        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_header_and_page_number)
        
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    
    def add_header_and_page_number(self, canvas, doc):
        self.add_header(canvas, doc)
        self.add_page_number(canvas, doc) 
    
    def add_page_number(self, canvas, doc):
       
        page_number = canvas.getPageNumber()
        total_pages = self.page_count
        text = f"page {page_number}  from {total_pages}"
       
        #arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        #pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
        canvas.setFont('Arabic', 12)
        
        text =  reshape(f"page: {page_number}")
        canvas.drawString(doc.width - 300, doc.bottomMargin - 65, text)
        
        line="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin-50, line)
        
        title_footer = get_display(reshape("برنامج الاصول")) 
        canvas.drawString(doc.width -40, doc.bottomMargin-65, title_footer)
        
        line_header="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin+490, line_header)
        
        title_header = get_display(reshape("المبادرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width-40, doc.bottomMargin+470, title_header)
        
        title_header_company = get_display(reshape("جمعية تنمية المجتمعات المحلية والمشروعات الصغيرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width -240, doc.bottomMargin+500, title_header_company)
        

    def add_header(self, canvas, doc):
        reshaped_header = [get_display(reshape(item)) for item in  ["الفرع", "قيمة الاهلاك", "القيمة", "العدد", "السعر", "البيان", "التصنيف", "اسم الأصل", "رقم الأصل"]]
        header_style = self.get_table_style(colors.grey, colors.whitesmoke, colors.black, 8, doc.leftMargin, 10, 12)
        
        # تعيين أطوال الأعمدة بشكل مناسب
        col_widths = [60,40,65,35, 60, 214, 76, 77, 54]
       
        # إنشاء جدول الرأس مع تحديد أطوال الأعمدة
        header_table = self.create_table([reshaped_header], header_style, col_widths)
        
        header_table.wrapOn(canvas, doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin+5, doc.height +22+ doc.topMargin - header_table._height)

    def create_table(self, data, style, colWidths=None):
        table = Table(data, colWidths=colWidths) if colWidths else Table(data)
        table.setStyle(style)
        return table

    def get_table_style(self, background, text_color, font_color, font_size, padding, right_padding, bottom_padding=0, col_widths=None):
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), background),
            ('TEXTCOLOR', (0, 0), (-1, 0), text_color),
            ('FONTSIZE', (0, 0), (-1, 0), font_size),
            ('RIGHTPADDING', (0, 0), (-1, -1), right_padding),
            ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_padding),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]
        
        if col_widths:
            style.append(('COLWIDTHS', (0, 0), (-1, -1), col_widths))
        
        return TableStyle(style)
 
class DestructionReportView(View):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.page_count = 0
        
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        asset_item_id = kwargs.get('asset_item_id')
        items = get_object_or_404(AssetItems, pk=asset_item_id)
        destructions = Destruction.objects.filter(asset_item_id=asset_item_id).values(
            'asset_item', 'destruction_start_month', 'destruction_end_month', 'destruction_percent', 'destruction_value',
            'branch_name__branch_name'
        )

        data = [
           ["الفرع", "قيمة الاهلاك", "نسبة الاهلاك", "نهاية الاهلاك", "بداية الاهلاك ", "رقم الاهلاك"],
            *[
                [
                    split_text(destruction['branch_name__branch_name'],15),
                    destruction['destruction_value'],
                    destruction['destruction_percent'],
                    destruction['destruction_end_month'],
                    destruction['destruction_start_month'],
                    destruction['asset_item'],
                ]
                for destruction in destructions
            ]
        ]

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="destruction_report_{asset_item_id}.pdf"'

        buffer = BytesIO()
        #doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=100, bottomMargin=100)

        arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))

        pdf = self.build_pdf(buffer, doc, items, data)

        response.write(pdf)

        return response
   
        
    def build_pdf(self, buffer, doc, items, data):
        reshaped_data = [[get_display(reshape(str(item))) for item in row] for row in data]

        # عنوان التقرير
        title = [
            [get_display(reshape("تقرير اهلاك الاصول"))],
            [get_display(reshape(f"رقم الاصل: {items.asset_number}"))],
            [get_display(reshape(f"اسم الاصل: {items.asset_name}"))],
            [get_display(reshape(f" التصنيف: {items.asset_group}"))],
            [get_display(reshape(f" البيان: {items.asset_description}"))],
            [get_display(reshape(f" الفرع: {items.branch_name}"))],
        ]
        footer_text = [
            [get_display(reshape("ملخص الاهلاك"))],
            [get_display(reshape(f" بداية الاهلاك: {items.destruction_start_month}"))],
            [get_display(reshape(f" نهاية الاهلاك: {items.destruction_end_month}"))],
            [get_display(reshape(f"قيمة الاهلاك : {items.destruction_value}"))],
        ]

        title_col_widths = [max(len(cell) for cell in row) for row in title]
        footer_col_widths = [max(len(cell) for cell in row) for row in footer_text]
        table_right_padding = -300

        title_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), table_right_padding),
        ])

        footer_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 300),
        ])

        # إعداد جداول العنوان والفوتر بالأنماط المحددة
        title_table = Table(title, colWidths=title_col_widths)
        title_table.setStyle(title_style)

        footer_table = Table(footer_text, colWidths=footer_col_widths)
        footer_table.setStyle(footer_style)

        # إعداد بيانات الجدول بالأنماط المحددة
        col_widths = [102, 111, 110, 110, 112, 106]
        #data_table = Table(reshaped_data, colWidths=col_widths)
        
        data_table = Table(reshaped_data, colWidths=col_widths)
        data_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 50),
            
           
           
        ])
        data_table.setStyle(data_style)

        # إعداد قالب لعرض العنوان والفوتر في الأعلى
        title_footer_template = Table([
            [title_table, footer_table]
        ], colWidths=[doc.width/2, doc.width/2])

        # إعداد الأنماط للتيتل والفوتر في القالب
        template_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), -40),
        ])
        title_footer_template.setStyle(template_style)
     

        elements = [title_footer_template, data_table]
        
        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_header_and_page_number)
       
        
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


    def add_header_and_page_number(self, canvas, doc):
        self.add_header(canvas, doc)
        self.add_page_number(canvas, doc) 
        
    
    
    def add_page_number(self, canvas, doc):
       
        page_number = canvas.getPageNumber()
        total_pages = self.page_count
        text = f"page {page_number}  from {total_pages}"
       
        #arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        #pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
        canvas.setFont('Arabic', 12)
        
        text =  reshape(f"page: {page_number}")
        canvas.drawString(doc.width - 300, doc.bottomMargin - 65, text)
        
        line="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin-50, line)
        
        title_footer = get_display(reshape("برنامج الاصول")) 
        canvas.drawString(doc.width -40, doc.bottomMargin-65, title_footer)
        
        line_header="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin+490, line_header)
        
        title_header = get_display(reshape("المبادرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width-40, doc.bottomMargin+470, title_header)
        
        title_header_company = get_display(reshape("جمعية تنمية المجتمعات المحلية والمشروعات الصغيرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width -240, doc.bottomMargin+500, title_header_company)
        
    
    def add_header(self, canvas, doc):
        reshaped_header = [get_display(reshape(item)) for item in ["الفرع", "قيمة الاهلاك", "نسبة الاهلاك", "نهاية الاهلاك", "بداية الاهلاك ", "رقم الاهلاك"]]
        header_style = self.get_table_style(colors.grey, colors.whitesmoke, colors.black, 8, doc.leftMargin, 10, 12)
        
        # تعيين أطوال الأعمدة بشكل مناسب
        col_widths = [102, 111, 110, 110, 112, 106]
       
        # إنشاء جدول الرأس مع تحديد أطوال الأعمدة
        header_table = self.create_table([reshaped_header], header_style, col_widths)
        
        header_table.wrapOn(canvas, doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin+20, doc.height +22+ doc.topMargin - header_table._height)

    def create_table(self, data, style, colWidths=None):
        table = Table(data, colWidths=colWidths) if colWidths else Table(data)
        table.setStyle(style)
        return table

    def get_table_style(self, background, text_color, font_color, font_size, padding, right_padding, bottom_padding=0, col_widths=None):
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), background),
            ('TEXTCOLOR', (0, 0), (-1, 0), text_color),
            ('FONTSIZE', (0, 0), (-1, 0), font_size),
            ('RIGHTPADDING', (0, 0), (-1, -1), right_padding),
            ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_padding),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            
           
        ]
        
        if col_widths:
            style.append(('COLWIDTHS', (0, 0), (-1, -1), col_widths))
        
        return TableStyle(style)
    
class TranferReportView(View):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.page_count = 0
        
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        transfer_destruction_id = kwargs.get('transfer_destruction_id')
        items = get_object_or_404(Transfer, pk=transfer_destruction_id)
        
        #transfer_asset_id= kwargs.get('transfer_asset_id')
        items_asset = get_object_or_404(TransferAsset, transfer_asset_id=transfer_destruction_id)
        
        transfers = TransferDestructionDetails.objects.filter(transfer_destruction_id=transfer_destruction_id).values(
            'transfer_destruction', 'asset__asset_name',
            'source_branch_destruction__branch_name', 'destination_branch_destruction__branch_name', 
            'transfer_date_destruction', 'destruction__destruction_value',
            'destruction__destruction_end_month','destruction__destruction_start_month'
            
        )
        
        data = [
           ["قيمة الاهلاك","نهاية الاهلاك","بداية الاهلاك","تاريخ التحويل",
            "الفرع الهدف","الفرع المصدر","اسم الاصل", "رقم التحويل"],
            *[
                [
                    transfer['destruction__destruction_value'],
                    transfer['destruction__destruction_end_month'],
                    transfer['destruction__destruction_start_month'],
                    transfer['transfer_date_destruction'],
                    transfer['destination_branch_destruction__branch_name'],
                    transfer['source_branch_destruction__branch_name'],
                    transfer['asset__asset_name'],
                    transfer['transfer_destruction'],
                ]
                for transfer in transfers
            ]
        ]

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="transfer_report_{transfer_destruction_id}.pdf"'

        buffer = BytesIO()
        #doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=100, bottomMargin=100)

        arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))

        pdf = self.build_pdf(buffer, doc, items, items_asset, data)

        response.write(pdf)

        return response
   
        
    def build_pdf(self, buffer, doc, items,items_asset, data):
        reshaped_data = [[get_display(reshape(str(item))) for item in row] for row in data]

        # عنوان التقرير
        title = [
            
            [get_display(reshape("تقرير تحويل الاصول"))],
            [get_display(reshape(f" رقم الاصل: {items.asset}"))],
            [get_display(reshape(f" الفرع المصدر: {items.source_branch}"))],
            [get_display(reshape(f"الفرع الهدف : {items.destination_branch}"))],
            [get_display(reshape(f"تاريخ التحويل : {items.transfer_date}"))],
            [get_display(reshape(f"بيان التحويل : {items.transfer_title}"))],
            
           
        ]
        footer_text = [
            [get_display(reshape("بيانات الاصل المحول"))],
            [get_display(reshape(f"رقم التحويل: {items_asset.transfer_asset}"))],
            [get_display(reshape(f"رقم الاصل: {items_asset.asset}"))],
            [get_display(reshape(f" الفرع المصدر: {items_asset.source_branch_asset}"))],
            [get_display(reshape(f" الفرع الهدف: {items_asset.destination_branch_asset}"))],
            [get_display(reshape(f" تاريخ التحويل: {items_asset.transfer_date_asset}"))],
           
        ]

        title_col_widths = [max(len(cell) for cell in row) for row in title]
        footer_col_widths = [max(len(cell) for cell in row) for row in footer_text]
        table_right_padding = -300
        
        title_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), table_right_padding),
        ])

        footer_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 300),
            
        ])

        # إعداد جداول العنوان والفوتر بالأنماط المحددة
        title_table = Table(title, colWidths=title_col_widths)
        title_table.setStyle(title_style)

        footer_table = Table(footer_text, colWidths=footer_col_widths)
        footer_table.setStyle(footer_style)

        # إعداد بيانات الجدول بالأنماط المحددة
        col_widths = [80, 80, 80, 80, 70, 100, 100, 100, 70]
        data_table = Table(reshaped_data, colWidths=col_widths)
        #data_table = Table(reshaped_data)
        data_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            
            ('COLWIDTHS', (0, 0), (-1, -1), col_widths)
            
           
           
        ])
      
        data_table.setStyle(data_style)

        # إعداد قالب لعرض العنوان والفوتر في الأعلى
        title_footer_template = Table([
            [title_table, footer_table]
        ], colWidths=[doc.width/2, doc.width/2])

        # إعداد الأنماط للتيتل والفوتر في القالب
        template_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), -40),
            
        ])
        title_footer_template.setStyle(template_style)
     
        
        elements = [title_footer_template, data_table]
        
        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_header_and_page_number)
       
        
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


    def add_header_and_page_number(self, canvas, doc):
        self.add_header(canvas, doc)
        self.add_page_number(canvas, doc) 
        
    
    
    def add_page_number(self, canvas, doc):
       
        page_number = canvas.getPageNumber()
        total_pages = self.page_count
        text = f"page {page_number}  from {total_pages}"
       
        #arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        #pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
        canvas.setFont('Arabic', 12)
        
        text =  reshape(f"page: {page_number}")
        canvas.drawString(doc.width - 300, doc.bottomMargin - 65, text)
        
        line="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin-50, line)
        
        title_footer = get_display(reshape("برنامج الاصول")) 
        canvas.drawString(doc.width -40, doc.bottomMargin-65, title_footer)
        
        line_header="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin+490, line_header)
        
        title_header = get_display(reshape("المبادرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width-40, doc.bottomMargin+470, title_header)
        
        title_header_company = get_display(reshape("جمعية تنمية المجتمعات المحلية والمشروعات الصغيرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width -240, doc.bottomMargin+500, title_header_company)
        
    
    def add_header(self, canvas, doc):
        reshaped_header = [get_display(reshape(item)) for item in ["قيمة الاهلاك","نهاية الاهلاك","بداية الاهلاك","تاريخ التحويل", "الفرع الهدف","الفرع المصدر","رقم الاصل", "رقم التحويل"]]
        header_style = self.get_table_style(colors.grey, colors.whitesmoke, colors.black, 8, doc.leftMargin, 10, 12)
        
        # تعيين أطوال الأعمدة بشكل مناسب
       
        #col_widths = [70, 70, 70, 70, 60, 60, 60, 50, 60]
        col_widths = [80, 80, 80, 80, 70, 100, 100, 100, 70]
        # إنشاء جدول الرأس مع تحديد أطوال الأعمدة
        header_table = self.create_table([reshaped_header], header_style, col_widths)
        
        header_table.wrapOn(canvas, doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin+1, doc.height +22+ doc.topMargin - header_table._height)

    def create_table(self, data, style, colWidths=None):
        table = Table(data, colWidths=colWidths) if colWidths else Table(data)
        table.setStyle(style)
        return table

    def get_table_style(self, background, text_color, font_color, font_size, padding, right_padding, bottom_padding=0, col_widths=None):
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), background),
            ('TEXTCOLOR', (0, 0), (-1, 0), text_color),
            ('FONTSIZE', (0, 0), (-1, 0), font_size),
            ('RIGHTPADDING', (0, 0), (-1, -1), right_padding),
            ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_padding),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            
           
        ]
        
        if col_widths:
            style.append(('COLWIDTHS', (0, 0), (-1, -1), col_widths))
        
        return TableStyle(style)
    
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
    #return start_date.text()

class ReportsAssetReportView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_count = 0
        self.start_date=0
        self.end_date=0
        self.asset_group=0
        self.branch=0
        self.total_price=0
   
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get('end_date')
        asset_group = request.GET.get('asset_group')
        print('aaaaaaaaaaaaa', asset_group)
       
        
        branch = request.GET.get('branch')
        #start_date = form.cleaned_data['start_date']
        
        self.start_date=start_date
        self.end_date=end_date
        if asset_group:
            asset_group_name = AssetGroup.objects.get(id=asset_group)
            self.asset_group=asset_group_name
        else:
            self.asset_group='كل التصنيفات'
        branch_name = Branch.objects.get(id=branch)
        self.branch=branch_name
        if asset_group:
            assets = AssetItems.objects.filter(
                invoice_number__invoice_date__range=(start_date, end_date),
                branch_name=branch,
                asset_group=asset_group
        )
        else:
             assets = AssetItems.objects.filter(
                invoice_number__invoice_date__range=(start_date, end_date),
                branch_name=branch,
               
             )
        total_price = sum(asset.asset_price for asset in assets)
        self.total_price = total_price
        # دورة لحساب مجموع الاهلاك لكل تصنيف
        assets_by_group = defaultdict(list)
        total_by_group = defaultdict(float)
        for asset in assets:
            assets_by_group[asset.asset_group].append(asset)
            total_by_group[asset.asset_group] += asset.asset_price

        data = [
           ["الفرع","السعر الاجمالي","سعر الوحدة","عدد","تاريخ الشراء",
           "البيان","التصنيف","اسم الاصل","رقم الاصل","رقم الفاتورة"],
           #[get_display(reshape("إجمالي السعر")), "", "", "", "", "", "", "", "", total_price],
            
            *[
                [
                    split_text(str(asset.branch_name),10),
                    asset.asset_price,
                    asset.price,
                    asset.count,
                    asset.invoice_number.invoice_date,
                    split_text(str(asset.asset_description),30),
                    split_text(str(asset.asset_group),20),
                    
                    asset.asset_name,
                    asset.asset_number,
                    split_text(str(asset.invoice_number.invoice_number),10),
                   
                    
                ]
                for asset in assets
            ],
            # إضافة مجموع كل تصنيف إلى القائمة
                    *[
                        [
                            "",  # الفراغ لعمود الفرع
                            "",
                            round(total_by_group[asset_group],2),  # إضافة مجموع كل تصنيف هنا
                            "",
                            "",  # الفراغ لعمود نهاية الاهلاك
                            "",
                            split_text(str(asset_group),20),  # عرض اسم التصنيف هنا
                            "",
                            "",
                            "",  # الفراغ لعمود رقم الاصل
                        ]
                        for asset_group in assets_by_group.keys()
                    ]
                ]
                    
        

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="asset_report.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=100, bottomMargin=100)

        arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))

        pdf = self.build_pdf(buffer, doc, data)

        response.write(pdf)
        

        return response

    def build_pdf(self, buffer, doc, data):
        reshaped_data = [[get_display(reshape(str(item))) for item in row] for row in data]

        # عنوان التقرير
        title = [
            [get_display(reshape("تقرير الاصل "))],
            [get_display(reshape(f"تاريخ الشراء من: {self.start_date} الي: {self.end_date}"))],
            [get_display(reshape(f"التصنيف: {self.asset_group}"))],
            [get_display(reshape(f"الفرع: {self.branch} "))],
            
        ]
        footer_text = [
            [get_display(reshape("ملخص تقرير الاصول"))],
            
            [get_display(reshape(f"اجمالي قيمة الاصول {self.total_price}"))],
            
            
        ]

        title_col_widths = [max(len(cell) for cell in row) for row in title]
        footer_col_widths = [max(len(cell) for cell in row) for row in footer_text]
        
        title_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), -700),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ])

        footer_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), -500),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ])

        # إعداد جداول العنوان والفوتر بالأنماط المحددة
        title_table = Table(title, colWidths=title_col_widths)
        title_table.setStyle(title_style)

        footer_table = Table(footer_text, colWidths=footer_col_widths)
        footer_table.setStyle(footer_style)

        # إعداد بيانات الجدول بالأنماط المحددة
        col_widths = [80, 80, 70, 50, 80,150, 70, 70, 50,50]
        data_table = Table(reshaped_data, colWidths=col_widths)
       
        data_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 50),
            
           
           
        ])
        data_table.setStyle(data_style)
        data_table.setStyle(data_style)

        # إعداد قالب لعرض العنوان والفوتر في الأعلى
        title_footer_template = Table([
            [title_table, footer_table]
        ], colWidths=[doc.width/2, doc.width/2])

         # إعداد الأنماط للتيتل والفوتر في القالب
        template_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), -40),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            
        ])
        title_footer_template.setStyle(template_style)

        elements = [title_footer_template, data_table]
        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_header_and_page_number)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def add_header_and_page_number(self, canvas, doc):
        self.add_header(canvas, doc)
        self.add_page_number(canvas, doc) 
        
    
    
    def add_page_number(self, canvas, doc):
       
        page_number = canvas.getPageNumber()
        total_pages = self.page_count
        text = f"page {page_number}  from {total_pages}"
       
        #arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        #pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
        canvas.setFont('Arabic', 12)
        
        text =  reshape(f"page: {page_number}")
        canvas.drawString(doc.width - 300, doc.bottomMargin - 65, text)
        
        line="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin-50, line)
        
        title_footer = get_display(reshape("برنامج الاصول")) 
        canvas.drawString(doc.width -40, doc.bottomMargin-65, title_footer)
        
        line_header="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin+490, line_header)
        
        title_header = get_display(reshape("المبادرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width-40, doc.bottomMargin+470, title_header)
        
        title_header_company = get_display(reshape("جمعية تنمية المجتمعات المحلية والمشروعات الصغيرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width -240, doc.bottomMargin+500, title_header_company)
        
    
    def add_header(self, canvas, doc):
        reshaped_header = [get_display(reshape(item)) for item in  ["الفرع","السعر الاجمالي",
            "سعر الوحدة","عدد","تاريخ الشراء","البيان","التصنيف","اسم الاصل","رقم الاصل","رقم الفاتورة"]]
        header_style = self.get_table_style(colors.grey, colors.whitesmoke, colors.black, 8, doc.leftMargin, 10, 12)
        
        # تعيين أطوال الأعمدة بشكل مناسب
       
        #col_widths = [70, 70, 70, 70, 60, 60, 60, 50, 60]
        col_widths = [80, 80, 70, 50, 80,150, 70, 70, 50,50]
        # إنشاء جدول الرأس مع تحديد أطوال الأعمدة
        header_table = self.create_table([reshaped_header], header_style, col_widths)
        
        header_table.wrapOn(canvas, doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin-30, doc.height +22+ doc.topMargin - header_table._height)

    def create_table(self, data, style, colWidths=None):
        table = Table(data, colWidths=colWidths) if colWidths else Table(data)
        table.setStyle(style)
        return table

    def get_table_style(self, background, text_color, font_color, font_size, padding, right_padding, bottom_padding=0, col_widths=None):
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), background),
            ('TEXTCOLOR', (0, 0), (-1, 0), text_color),
            ('FONTSIZE', (0, 0), (-1, 0), font_size),
            ('RIGHTPADDING', (0, 0), (-1, -1), right_padding),
            ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_padding),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            
           
        ]
        
        if col_widths:
            style.append(('COLWIDTHS', (0, 0), (-1, -1), col_widths))
        
        return TableStyle(style)
    
def destruction_report(request):
    #form = AssetReportForm(request.GET)
    #assets = []
    initial_data = {'start_date': '2000-01-01'}
    initial_data = {'end_date': datetime.today().date()}
    form = DestructionReportForm(request.GET or None, initial=initial_data)
    destructions = []

    if form.is_valid():
        #start_date = form.cleaned_data['start_date']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        asset_group = form.cleaned_data['asset_group']
        branch = form.cleaned_data['branch']

        destructions = Destruction.objects.filter(
            destruction_start_month__range=(start_date, end_date),
            #asset_group=asset_group,
            branch_name=branch
        )
       
    return render(request, 'reports/report_destruction.html', {'form': form, 'destructions': destructions})
    #return start_date.text()
    
from .forms import DestructionReportForm
class ReportsDestructionReportView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_count = 0
        self.start_date=0
        self.end_date=0
        self.asset_group=0
        self.branch=0
        self.total_price=0
   
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        
        form = DestructionReportForm(request.GET)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            asset_group = form.cleaned_data['asset_group']
            branch = form.cleaned_data['branch']
            option = form.cleaned_data['option']
            #print('aaaaaaab', start_date,end_date, branch, option)
            #start_date = request.GET.get("start_date")
            #end_date = request.GET.get('end_date')
            #asset_group = request.GET.get('asset_group')
            #branch = request.GET.get('branch')
            #start_date = form.cleaned_data['start_date']
            
            

           
            self.start_date=start_date
            self.end_date=end_date
            if asset_group:
                asset_group_name = AssetGroup.objects.get(id=asset_group)
                self.asset_group=asset_group_name
            else:
                self.asset_group='كل التصنيفات'
            branch_name = Branch.objects.get(id=branch)
            self.branch=branch_name
            
            if asset_group:
                assets = Destruction.objects.filter(
                    destruction_start_month__range=(start_date, end_date),
                    branch_name=branch,
                    asset_item__asset_group=asset_group)
            else:
                assets = Destruction.objects.filter(
                    destruction_start_month__range=(start_date, end_date),
                    branch_name=branch,)
            total_price = sum(asset.destruction_value for asset in assets)
            self.total_price = round(total_price,2)
            
            
           
            if option == 'option1':
                 # دورة لحساب مجموع الاهلاك لكل تصنيف
                assets_by_group = defaultdict(list)
                total_by_group = defaultdict(float)
                for asset in assets:
                    assets_by_group[asset.asset_item.asset_group].append(asset)
                    total_by_group[asset.asset_item.asset_group] += asset.destruction_value

                data = [
                    ["الفرع","اجمالي الاهلاك", "قيمة الاعلاك", "عدد الاهلاكات", "نسبة الاهلاك", 
                     "نهاية الاهلاك","بداية الاهلاك",  "التصنيف", "رقم الاصل"],
               
                
                #[get_display(reshape("إجمالي السعر")), "", "", "", "", "", "", "", "", total_price],
                    
                    *[
                        [
                            split_text(str(asset.branch_name),10),
                            "",
                            asset.destruction_value,
                            "",
                            split_text(str(asset.destruction_percent),30),
                            split_text(str(asset.destruction_end_month),20),
                            
                            asset.destruction_start_month,
                            split_text(str(asset.asset_item.asset_group),30),
                            asset.asset_item,
                            
                        
                            
                        ]
                        for asset in assets
                    ],
                    # إضافة مجموع كل تصنيف إلى القائمة
                    *[
                        [
                            "",  # الفراغ لعمود الفرع
                            "",
                            round(total_by_group[asset_group],2),  # إضافة مجموع كل تصنيف هنا
                            "",
                            "",  # الفراغ لعمود نهاية الاهلاك
                            "",  # الفراغ لعمود بداية الاهلاك
                            "",
                            asset_group,  # عرض اسم التصنيف هنا
                            "",  # الفراغ لعمود رقم الاصل
                        ]
                        for asset_group in assets_by_group.keys()
                    ]
                ]
                    
            elif option == 'option2':
                
               # تجميع الأصول حسب كل عنصر فردي
                assets_by_item = defaultdict(list)
                total_by_item = defaultdict(float)
                first_destruction_dates = {}
                last_destruction_dates = {}
                destruction_counts = defaultdict(int)
                total_by_group = defaultdict(float)

                for asset in assets:
                    assets_by_item[asset.asset_item].append(asset)
                    total_by_item[asset.asset_item] += asset.destruction_value
                    total_by_group[asset.asset_item.asset_group] += asset.destruction_value

                    # حفظ تاريخ أول اهلاك وآخر اهلاك لكل عنصر
                    if asset.asset_item not in first_destruction_dates:
                        first_destruction_dates[asset.asset_item] = asset.destruction_start_month
                        last_destruction_dates[asset.asset_item] = asset.destruction_end_month
                    else:
                        if asset.destruction_start_month < first_destruction_dates[asset.asset_item]:
                            first_destruction_dates[asset.asset_item] = asset.destruction_start_month
                        if asset.destruction_end_month > last_destruction_dates[asset.asset_item]:
                            last_destruction_dates[asset.asset_item] = asset.destruction_end_month

                    # زيادة العداد لعدد الاهلاكات لكل عنصر
                    destruction_counts[asset.asset_item] += 1
                data = [
                    ["الفرع","اجمالي الاهلاك", "قيمة الاعلاك", "عدد الاهلاكات", "نسبة الاهلاك", 
                     "نهاية الاهلاك","بداية الاهلاك",  "التصنيف", "رقم الاصل"],
                ]
                
                # قائمة لتتبع الأصول التي تم معالجتها بالفعل
                processed_items = set()

                for asset in assets:
                    asset_item = asset.asset_item
                    # التحقق مما إذا كانت هذه الأصل تم معالجتها بالفعل
                    if asset_item in processed_items:
                        continue
                    
                    # إضافة بيانات الأصل إلى التقرير
                    data.append([
                        split_text(str(asset.branch_name), 10),
                        round(total_by_item[asset.asset_item], 2),  # إجمالي الاهلاك
                        asset.destruction_value,
                        destruction_counts[asset.asset_item],  # عدد الاهلاكات
                        split_text(str(asset.destruction_percent), 10),
                        split_text(str(last_destruction_dates[asset.asset_item]), 10),
                        split_text(str(first_destruction_dates[asset.asset_item]), 10),
                        split_text(str(asset.asset_item.asset_group), 10),
                        split_text(str(asset.asset_item.asset_number), 10),
                        
                        
                        
                        
                        
                        
                    ])
                    
                    # قم بإضافة الأصل إلى القائمة التي تتبع الأصول المعالجة
                    processed_items.add(asset_item)

                # إضافة صفوف الإجماليات لكل تصنيف
                for asset_group, total in total_by_group.items():
                    data.append([
                        "", round(total, 2), "", "", "", "", "", asset_group, "",
                    ])






                

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="destruction_report.pdf"'

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=50, rightMargin=50, topMargin=100, bottomMargin=100)

            arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
            pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))

            pdf = self.build_pdf(buffer, doc, data)

            response.write(pdf)
            

            return response

    def build_pdf(self, buffer, doc, data):
        reshaped_data = [[get_display(reshape(str(item))) for item in row] for row in data]

        # عنوان التقرير
        title = [
            [get_display(reshape("تقرير الاهلاك "))],
            [get_display(reshape(f"تاريخ الاهلاك من: {self.start_date} الي: {self.end_date}"))],
            [get_display(reshape(f"التصنيف: {self.asset_group}"))],
            [get_display(reshape(f"الفرع: {self.branch} "))],
            
        ]
        footer_text = [
            [get_display(reshape("ملخص تقرير الاهلاك"))],
            
            [get_display(reshape(f"اجمالي قيمة الاهلاك {self.total_price}"))],
            
            
        ]

        title_col_widths = [max(len(cell) for cell in row) for row in title]
        footer_col_widths = [max(len(cell) for cell in row) for row in footer_text]
        
        title_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), -200),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ])

        footer_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), -300),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ])

        # إعداد جداول العنوان والفوتر بالأنماط المحددة
        title_table = Table(title, colWidths=title_col_widths)
        title_table.setStyle(title_style)

        footer_table = Table(footer_text, colWidths=footer_col_widths)
        footer_table.setStyle(footer_style)

        # إعداد بيانات الجدول بالأنماط المحددة
        col_widths = [80,80, 80, 70, 70, 70,100,100]
        data_table = Table(reshaped_data, colWidths=col_widths)
       
        data_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 50),
            
           
           
        ])
        data_table.setStyle(data_style)
        data_table.setStyle(data_style)

        # إعداد قالب لعرض العنوان والفوتر في الأعلى
        title_footer_template = Table([
            [footer_table, title_table]
        ], colWidths=[doc.width/2, doc.width/2])

         # إعداد الأنماط للتيتل والفوتر في القالب
        template_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), -40),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            
        ])
        title_footer_template.setStyle(template_style)

        elements = [title_footer_template, data_table]
        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_header_and_page_number)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def add_header_and_page_number(self, canvas, doc):
        self.add_header(canvas, doc)
        self.add_page_number(canvas, doc) 
        
    
    
    def add_page_number(self, canvas, doc):
       
        page_number = canvas.getPageNumber()
        total_pages = self.page_count
        text = f"page {page_number}  from {total_pages}"
       
        #arabic_font_path = "fonts/arabic_font/din-next-lt-w23-bold-1.ttf"
        #pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
        canvas.setFont('Arabic', 12)
        
        text =  reshape(f"page: {page_number}")
        canvas.drawString(doc.width - 300, doc.bottomMargin - 65, text)
        
        line="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin-50, line)
        
        title_footer = get_display(reshape("برنامج الاصول")) 
        canvas.drawString(doc.width -40, doc.bottomMargin-65, title_footer)
        
        line_header="____________________________________________________"*2
        canvas.drawString(doc.width -620, doc.bottomMargin+490, line_header)
        
        title_header = get_display(reshape("المبادرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width-40, doc.bottomMargin+470, title_header)
        
        title_header_company = get_display(reshape("جمعية تنمية المجتمعات المحلية والمشروعات الصغيرة"))  # احتمال تغيير الشكل أيضًا
        canvas.drawString(doc.width -240, doc.bottomMargin+500, title_header_company)
        
    
    def add_header(self, canvas, doc):
       
        reshaped_header = [get_display(reshape(item)) for item in    ["الفرع","اجمالي الاهلاك", "قيمة الاعلاك", "عدد الاهلاكات", "نسبة الاهلاك", 
                     "نهاية الاهلاك","بداية الاهلاك",  "التصنيف", "رقم الاصل"]]
        header_style = self.get_table_style(colors.grey, colors.whitesmoke, colors.black, 8, doc.leftMargin, 10, 12)
        
        # تعيين أطوال الأعمدة بشكل مناسب
       
        #col_widths = [70, 70, 70, 70, 60, 60, 60, 50, 60]
        col_widths = [80,80, 80, 70, 70, 70,100,100]
        # إنشاء جدول الرأس مع تحديد أطوال الأعمدة
        header_table = self.create_table([reshaped_header], header_style, col_widths)
        
        header_table.wrapOn(canvas, doc.width, doc.topMargin)
        header_table.drawOn(canvas, doc.leftMargin-30, doc.height +22+ doc.topMargin - header_table._height)

    def create_table(self, data, style, colWidths=None):
        table = Table(data, colWidths=colWidths) if colWidths else Table(data)
        table.setStyle(style)
        return table

    def get_table_style(self, background, text_color, font_color, font_size, padding, right_padding, bottom_padding=0, col_widths=None):
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
            ('BACKGROUND', (0, 0), (-1, 0), background),
            ('TEXTCOLOR', (0, 0), (-1, 0), text_color),
            ('FONTSIZE', (0, 0), (-1, 0), font_size),
            ('RIGHTPADDING', (0, 0), (-1, -1), right_padding),
            ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_padding),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            
           
        ]
        
        if col_widths:
            style.append(('COLWIDTHS', (0, 0), (-1, -1), col_widths))
        
        return TableStyle(style)
    
    
    

    
    
