# Copyright (c) 2026, Sowmiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

# def before_print(doc, method=None):
#     doc.print_summary = (
#         f"{doc.customer_name} - "
#         f"{doc.start_date} to {doc.end_date}"
#     )


class RentalBooking(Document):
	def validate(self):
		self.validate_date()
		self.on_save()
		self.calculate_days()
		self.checkin_checkout_grade()
		self.overlap()

	def validate_date(self):
		if(self.start_date==self.end_date):
			frappe.throw(f"Start Date and End Date Connot be Same.")
		elif(self.start_date>self.end_date):
			frappe.throw("End Date cannot be less than Start Date.")

	def calculate_days(self):
		rental_total=0
		for item in self.items:
			if self.start_date and self.end_date:
				start = frappe.utils.getdate(self.start_date)
				end = frappe.utils.getdate(self.end_date)
				item.line_days = (end - start).days + 1
				item.line_amount=((item.line_days or 0)*(item.daily_rate or 0))
				rental_total+=item.line_amount
		self.rental_total=rental_total
		# frappe.msgprint(f"{self.rental_total}")

	def checkin_checkout_grade(self):
		damage_total=0
		damage_fee_per_grade_drop=frappe.db.get_single_value('Rentflow Settings','damage_fee_per_grade_drop') or 0
		grade={"New":1,"Good": 2,"Fair": 3,"Poor": 4,"Damaged": 5}
		for item in self.items:
			if(item.checkin_condition_grade and item.checkout_condition_grade):
				checkin=grade.get(item.checkin_condition_grade)
				checkout=grade.get(item.checkout_condition_grade)
				if(checkin>checkout):
					diff=checkin-checkout
					item.damage_fee=damage_fee_per_grade_drop*diff
					damage_total+=item.damage_fee
		self.damage_total=damage_total
		self.final_amount=self.rental_total+self.damage_total
		# frappe.msgprint(f"{self.final_amount}")
		# frappe.msgprint(f"{self.damage_total}")

	def overlap(self):
		for item in self.items:
			if item.equipment_unit:
				conflict=frappe.db.sql("""select rb.name from `tabRental Booking` rb inner join `tabBooking Item` bi on bi.parent = rb.name where rb.docstatus = 1
					and rb.name != %s and rb.status NOT IN ('Cancelled', 'Returned') and bi.equipment_unit = %s
					and rb.start_date <= %s and rb.end_date >= %s""",(self.name,item.equipment_unit,self.end_date,self.start_date),as_dict=True)
				if conflict:
					frappe.throw(f"Equipment Unit {item.equipment_unit} is booked {conflict[0]}")

	def on_save(self):
		for item in self.items:
			if item.category:
				daily_rate = frappe.db.get_value("Equipment Category",item.category,"daily_rate")
				# frappe.db.set_value("Booking Item",item.name,"daily_rate",daily_rate)
				item.daily_rate=daily_rate

	def before_submit(self):
		if self.status!="Confirmed":
			frappe.throw(f"Status is not set to confirmed.You cannot be able to submit the document.")
		if self.deposit_collected<=0:
			frappe.throw(f"Deposit Collected should be greater than 0.")
		self.overlap()

	def on_submit(self):
		for item in self.items:
			frappe.db.set_value("Equipment Unit",item.equipment_unit,"current_status","Reserved",update_modified=False)
			invoice=frappe.get_doc({
			'doctype':'Rental Invoice',
			'rental_booking':self.name,
			'rental_amount':self.rental_total,
			'damage_amount':self.damage_total,
			'total_amount':self.final_amount
			})
			invoice.insert(ignore_permissions=True)
		frappe.enqueue("rental.rental_management.doctype.rental_booking.rental_booking.send_booking_confirmation",booking_name=self.name,queue="short")

	def send_booking_confirmation(booking_name):
		booking = frappe.get_doc("Rental Booking", booking_name)
		frappe.sendmail(
		recipients=[booking.customer_email],
        subject=f"Booking Confirmed - {booking.name}",
        message=f"""
			Your rental booking {booking.name} has been confirmed.
            Start Date: {booking.start_date}
            End Date: {booking.end_date}
            Rental Total: {booking.rental_total}""",
			header=('Booking Confirmed'))
		
	def on_cancel(self):
		self.db_set("status","Cancelled")
		for item in self.items:
			frappe.db.set_value(
				"Equipment Unit",
				item.equipment_unit,
				"current_status",
				"Available"
			)
		invoice=frappe.db.get_value("Rental Invoice",{
			"rental_booking":self.name,
			"payment_status":"Unpaid"
		},"name")
		if invoice:
			invoice=frappe.get_doc("Rental Invoice",invoice)
			if invoice.docstatus==1:
				invoice.cancel()

	def on_trash(self):
		if self.status not in ("Cancelled","Draft"):
			frappe.throw("Status which are not in Cancelled or Draft can't be deleted")

	# RecursionError: maximum recursion depth exceeded
	# def on_update(self):
	# 	self.final_amount=self.rental_total+self.damage_total
	# 	self.save()

	# def before_print(self,doc):
	# 	self.print_summary = f"{doc.customer_name} - {doc.start_date} to {doc.end_date}"

@frappe.whitelist()
def get_shop_name():
	return frappe.db.get_single_value("RentFlow Settings","shop_name")

def before_print(doc, method=None,print_settings=None):
    doc.print_summary = (f"{doc.customer_name} - "f"{doc.start_date} to {doc.end_date}")




def rental_booking_query(user):
	if "Manager"==frappe.session.user:
		return ""
	if "Inspector"==frappe.session.user:
		# return """`tabRental Booking`.`handled_by` in(select `name` from `tabYard Staff` where user='{user}').format(user=frappe.db.escape(user)"""
		safe_user = frappe.db.escape(user)
		return f"`tabRental Booking`.handled_by in (select name from `tabYard Staff` where user = {safe_user})"
	return ""


@frappe.whitelist()
def get_booking_unsafe():
	doc=frappe.db.get_all("Rental Booking")

@frappe.whitelist()
def get_booking_safe():
	bookings = frappe.get_list("Rental Booking",
	    fields=["name","customer_name","customer_phone","customer_email","start_date","end_date","status","handled_by","rental_total"])
	if "Manager"==frappe.session.user:
			return bookings
	safe_bookings=[]
	for booking in bookings:
		safe_booking = {
            "name": booking["name"],
            "customer_name": booking["customer_name"],
            "start_date": booking["start_date"],
            "end_date": booking["end_date"],
            "status": booking["status"],
            "handled_by": booking["handled_by"],
            "rental_total": booking["rental_total"]
        }
		safe_bookings.append(safe_booking)
	return safe_bookings





