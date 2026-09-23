// Copyright (c) 2026, Sowmiya and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental Booking", {
	validate(frm) {
        if(frm.doc.start_date==frm.doc.end_date){
            frappe.throw("Start Date and End Date Connot be Same.");
        }
        if(frm.doc.start_date>frm.doc.end_date){
            frappe.throw("End Date cannot be less than Start Date.");
        }
	},
    before_submit(frm){
        
    }
});
