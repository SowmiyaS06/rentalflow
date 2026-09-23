# Copyright (c) 2026, Sowmiya and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EquipmentUnit(Document):
    def validate(self):
        self.autoname
    def autoname(self):
        ctgry_name = frappe.db.get_value("Equipment Category",self.category,"name")
        pre = ctgry_name[:3].upper()
        self.name = frappe.model.naming.make_autoname(f"{pre}-.#####")
