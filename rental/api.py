import frappe
def log_change(doc,method):
    if doc.doctype=="Audit":
        return
    frappe.get_doc({
        'doctype':"Audit",
        'doctype_name':doc.doctype,
        'document_name':doc.name,
        'action':method,
        'user':frappe.session.user,
        'timestamp':frappe.utils.now()
    }).insert(ignore_permissions=True)

def after_install():
    create_default_rentflow_settings()
    create_default_categories()
    frappe.msgprint("Installed Successfully!")

def create_default_rentflow_settings():
    settings=frappe.get_doc("Rentflow Settings")
    if not settings.shop_name:
        settings.shop_name="abc"
    if not settings.manager_email:
        settings.manager_email="sowmiyas@example.com"
    if not settings.default_deposit_percent:
        settings.default_deposit_percent=20
    if not settings.damage_fee_per_grade_drop:
        settings.damage_fee_per_grade_drop=200
    if not settings.late_fee_per_day:
        settings.late_fee_per_day=10
    settings.save(ignore_permissions=True)

def create_default_categories():
    categories = [
        {
            "category_name":"General",
            "daily_rate":100,
            "deposit_amount":100
        },
        {
            "category_name":"Electronics",
            "daily_rate":600,
            "deposit_amount":150
        },
        {
            "category_name":"Furniture",
            "daily_rate":750,
            "deposit_amount":250
        }
    ]

    for category in categories:
        if not frappe.db.exists("Equipment Category", category):
            doc = frappe.get_doc({
                "doctype": "Equipment Category",
                "category_name": category
            })
            doc.insert(ignore_permissions=True)

def get_overdue_returns():
    rental_booking = frappe.qb.DocType('Rental Booking')
    q = (frappe.qb.from_(rental_booking)
    .select(rental_booking.name, rental_booking.customer_name,rental_booking.end_date)
    .where(rental_booking.status=="Checked Out")
    .where(rental_booking.end_date<frappe.utils.today())
    .orderby(rental_booking.end_date))
    return q
