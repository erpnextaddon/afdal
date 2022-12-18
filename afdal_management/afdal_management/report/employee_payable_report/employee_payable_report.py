# Copyright (c) 2022, Afdal and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import erpnext
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 130,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Basic Salary"),
            "fieldname": "basic_salary",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Qty Commision"),
            "fieldname": "qty_commision",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Payment Commision 1%"),
            "fieldname": "payment_commisions",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Driver Commision"),
            "fieldname": "driver_commision",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Employee Share From Sales"),
            "fieldname": "employee_share",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Total Pay"),
            "fieldname": "total_pay",
            "fieldtype": "Currency",
            "width": 120,
        }
    ]

    return columns


def get_data(filters):
    data = []
    employee_share = 0
    employees = frappe.db.sql(
        """select sales_share_number,name,employee_name,basic_salary from `tabEmployee` where status = 'Active'""", as_dict=1)
    frappe.errprint(employees)
    
    total_sale = frappe.db.sql("""select sum(total) as total_sale from `tabSales Invoice` where docstatus = 1 and posting_date between '%s' and '%s'"""%(filters.from_date,filters.to_date),as_dict=1)
    if total_sale:
        total_sale = total_sale[0].total_sale

        grade_count = frappe.db.sql("""select sum(sales_share_number) as grade_count from `tabEmployee` where status = 'Active'""",as_dict=1)
        if grade_count:
            grade_count = grade_count[0].grade_count
            if grade_count:
                employee_share = total_sale / grade_count
    
    for employee in employees:
        flag = True
        row = frappe._dict()
        row.qty_commision = 0
        row.driver_commision = 0
        row.employee = employee.name
        row.employee_name = employee.employee_name
        row.basic_salary = employee.basic_salary
        row.payment_commisions = 0
        row.total_pay = 0
        row.employee_share = 0
        driver = frappe.db.get_value(
            "Driver", {'employee': employee.name}, 'name')
        frappe.errprint(driver)
        if driver:
            flag = False
            total_qty = 0
            invoice_qty = 0
            invoice_list = []
            driver_sales_data = frappe.db.sql("""select sii.parent as invoice ,item_code,qty,uom,rate,amount from `tabSales Invoice Item`  sii
                                        inner join `tabSales Invoice` si
                                            on si.name = sii.parent
                                    where si.docstatus = 1 and si.posting_date between '%s' and '%s'
                                        and driver='%s'""" % (filters.from_date, filters.to_date, driver),as_dict=1)
            
            for item in driver_sales_data:
                invoice_list.append(item.invoice)
                if item.uom == 'Carton':
                    total_qty = total_qty + item.qty
                else:
                    uom_conversion = frappe.db.sql(
                        """select uom,conversion_factor from `tabUOM Conversion Detail` where uom='Carton'""", as_dict=1)
                    if uom_conversion:
                        conversion_factor = uom_conversion[0].conversion_factor or 0.0        
                        total_qty = total_qty + (item.qty / conversion_factor)
            
            invoice_qty = len(set(invoice_list))
            row.driver_commision = (invoice_qty * 1.3) + (total_qty * 0.05)

        
        sales_person = frappe.db.get_value(
                "Sales Person", {'employee': employee.name}, 'name')
        if sales_person:
            if sales_person:
                Flag = False
                total_qty = 0
                invoice_qty = 0
                salesperson_sales_data = frappe.db.sql("""select item_code,qty,uom,rate,amount from `tabSales Invoice Item`  sii
                                        inner join `tabSales Invoice` si
                                            on si.name = sii.parent
                                    where si.docstatus = 1 and si.posting_date between '%s' and '%s'
                                        and sales_person='%s' and selling_price_list != "قائمة مبيعات الجملة" """ % (filters.from_date, filters.to_date, sales_person),as_dict=1)
                frappe.errprint(salesperson_sales_data)
                frappe.errprint('sales')
                frappe.errprint(sales_person)
                for item in salesperson_sales_data:
                    if item.uom == 'Carton':
                        total_qty = total_qty + item.qty
                    else:
                        uom_conversion = frappe.db.sql(
                            """select uom,conversion_factor from `tabUOM Conversion Detail` where uom='Carton'""", as_dict=1)
                        if uom_conversion:
                            conversion_factor = uom_conversion[0].conversion_factor or 0.0
                            total_qty = total_qty + item.qty / conversion_factor

                frappe.errprint(total_qty)
                if total_qty > 2500 and total_qty <= 3000:
                    row.qty_commision = (total_qty - 2500)*0.12
                elif total_qty > 3000 and total_qty <= 3500:
                    row.qty_commision = ((total_qty - 3000)*0.2) + 60
                elif total_qty > 3500 and total_qty <= 4000:
                    row.qty_commision = ((total_qty - 3500)*0.25) + 160
                elif total_qty > 4000 and total_qty <= 4500:
                    row.qty_commision = ((total_qty - 4000)*0.3) + 285
                elif total_qty > 4500:
                    row.qty_commision = ((total_qty - 4500)*0.5) + 435

                payment_details = frappe.db.sql("""select 
                                                reference_doctype,
                                                reference_name,
                                                sum(allocated_amount) as allocated
                                            from `tabPayment Entry Reference` per
                                                inner join `tabPayment Entry` pe
                                                on per.parent = pe.name
                                            inner join `tabSales Invoice` si
                                                on si.name = per.reference_name
                                            where pe.docstatus = 1 and pe.posting_date between '%s' and '%s'
                                                and per.reference_doctype = 'Sales Invoice' and si.sales_person = '%s'
                                                """%(filters.from_date,filters.to_date,sales_person),as_dict=1)

                if payment_details:
                    paid_amount = payment_details[0].allocated or 0.0
                    if paid_amount:
                        row.payment_commisions = (paid_amount * 1)/100
                
                                                
        
        
        row.employee_share = employee.sales_share_number *  employee_share
        row.total_pay = row.qty_commision + row.driver_commision + row.basic_salary + row.payment_commisions + row.employee_share

        data.append(row)


    return data
