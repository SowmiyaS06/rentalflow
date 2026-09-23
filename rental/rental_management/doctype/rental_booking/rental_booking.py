# Copyright (c) 2026, Sowmiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document 

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
			if item.equivalent_unit:
				conflict=frappe.db.sql("""select rb.name from `tabRental Booking` rb inner join `tabBooking Item` bi on bi.parent = rb.name where rb.docstatus = 1
					and rb.name != %s and rb.status NOT IN ('Cancelled', 'Returned') and bi.equipment_unit = %s
					and rb.start_date <= %s and rb.end_date >= %s""",(self.name,item.equipment_unit,self.end_date,self.start_date),as_dict=True)
				if conflict:
					frappe.throw(f"Equipment Unit {item.equipmet_unit} is booked {conflict[0]}")

	def on_save(self):
		for item in self.items:
			if item.category:
				daily_rate = frappe.db.get_value("Equipment Category",item.category,"daily_rate")
				# frappe.db.set_value("Booking Item",item.name,"daily_rate",daily_rate)
				item.daily_rate=daily_rate





