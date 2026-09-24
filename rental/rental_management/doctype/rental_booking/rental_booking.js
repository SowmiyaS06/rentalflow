// Copyright (c) 2026, Sowmiya and contributors
// For license information, please see license.txt


frappe.ui.form.on("Rental Booking", {
    setup(frm) {
        frm.set_query("equipment_unit", "items", function () {
            return {
                filters: {
                    current_status: "Available"
                }
            };
        });
    },
    refresh(frm) {
    if (frm.doc.status === "Draft"){frm.dashboard.add_indicator("Draft", "orange");}
    else if (frm.doc.status === "Confirmed"){frm.dashboard.add_indicator("Confirmed", "blue");}
    else if (frm.doc.status === "Checked Out"){frm.dashboard.add_indicator("Checked Out", "green");}
    else if (frm.doc.status === "Returned"){frm.dashboard.add_indicator("Returned", "gray");}
    else if (frm.doc.status === "Cancelled") {frm.dashboard.add_indicator("Cancelled", "red");}
    if (frm.doc.status === "Checked Out"){
        frm.add_custom_button("Log Return",() => {
            frappe.msgprint("Log Return button got clicked.")
        });
    }
},
start_date(frm){calculate_days(frm)},
end_date(frm){calculate_days(frm)}
});
frappe.ui.form.on("Booking Item", {
    equipment_unit(frm, cdt, cdn) {
        calculate_child(frm, cdt, cdn);
    },
    line_days(frm, cdt, cdn) {
        calculate_child(frm, cdt, cdn);
    },
    daily_rate(frm, cdt, cdn) {
        calculate_child(frm, cdt, cdn);
    }
});

function calculate_days(frm){
    if (!frm.doc.start_date || !frm.doc.end_date) {return;}
    let start=frappe.datetime.str_to_obj(frm.doc.start_date);
    let end=frappe.datetime.str_to_obj(frm.doc.end_date);
    line_days=Math.floor((end-start)/(1000*60*60*24))+1;
    if(line_days>30){
        frappe.show_alert({
            message:"Line Days exceed 30 days",
            indicator:"orange"
        });
    }
}

function calculate_child(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const days = row.line_days||0;
    const rate = row.daily_rate|| 0;
    frappe.model.set_value(cdt,cdn,"line_amount",days * rate);
}
