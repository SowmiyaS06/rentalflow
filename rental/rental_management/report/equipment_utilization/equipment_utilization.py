# Copyright (c) 2026, Sowmiya and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	columns = [
		        {
            "label": "Category",
            "fieldname": "category",
            "fieldtype": "Link",
            "options": "Equipment Category"
        },
        {
            "label": "Total Units",
            "fieldname": "total_units",
            "fieldtype": "Int"
        },
        {
            "label": "Days Rented",
            "fieldname": "days_rented",
            "fieldtype": "Int"
        },
        {
            "label": "Utilization %",
            "fieldname": "utilization",
            "fieldtype": "Percent"
        },
        {
            "label": "Revenue",
            "fieldname": "revenue",
            "fieldtype": "Currency"
        },
        {
            "label": "Damage Incidents",
            "fieldname": "damage_incidents",
            "fieldtype": "Int"
        }
	]
	bookings=frappe.get_list("Rental Booking",fields=["name","start_date","end_date","rental_total"])
	categories={}
	for booking in bookings:
		items=frappe.get_list("Booking Item",filters={"parent":booking.name},fields=["equipment_unit","category","line_days","line_amount","damage_fee"])
	for item in items:
		category=item.category
		if category not in categories:
			categories[category] = {
                    "category": category,
                    "total_units": 0,
                    "days_rented": 0,
                    "revenue": 0,
                    "damage_incidents": 0
                }
		categories[category]["total_units"] += 1
		categories[category]["days_rented"] += (item.line_days or 0)
		categories[category]["revenue"] += (item.line_amount or 0)
		# if (item.damage_fee or 0) > 0:
		# 	categories[category]["damage_incidents"] += 1
		from_date = frappe.utils.getdate(filters.get("from_date"))
		to_date = frappe.utils.getdate(filters.get("to_date"))
		total_days = (to_date - from_date).days + 1
		for row in categories.values():
			if total_days:
				row["utilization"] = (row["days_rented"] / total_days) * 100
			else:
				row["utilization"] = 0
		
	return columns


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Column 1"),
			"fieldname": "column_1",
			"fieldtype": "Data",
		},
		{
			"label": _("Column 2"),
			"fieldname": "column_2",
			"fieldtype": "Int",
		},
	]


def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	return [
		["Row 1", 1],
		["Row 2", 2],
	]
