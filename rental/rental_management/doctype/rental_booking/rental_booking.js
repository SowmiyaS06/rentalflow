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
            let fields=[]
            frm.doc.items.forEach(item=>{
                fields.push({
                    label:item.equipment_unit,
                    fieldname:item.name,
                    fieldtype:"Select",
                    options:"New\nGood\nFair\nPoor\nDamaged",
                    default:item.checkout_condition_grade,
                    reqd:1

                });
            });
            fields.push({
                label:"Notes",
                fieldname:"notes",
                fieldtype:"Small Text"
            })
    let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: fields,
    size: 'small', // small, large, extra-large 
    primary_action_label: 'Submit',
    primary_action(values) {
    let grade={"New":1,"Good":2,"Fair":3,"Poor":4,"Damaged":5};
    let drop = false;
    frm.doc.items.forEach(item => {
        let checkout =item.checkout_condition_grade;
        let abc =values[item.name];
        if (grade[abc] > grade[checkout]) {
            drop = true;
         }
        frappe.model.set_value(item.doctype,item.name,"checkin_condition_grade",returned);
        });
        if (drop && !values.notes) {
            frappe.throw("Notes are required when the condition has dropped.");
        }
        dialog.hide();
        frm.trigger("start_date");
     }
});
d.show();
// frm.trigger("start_date");
        });
    }
    frm.add_custom_button("Transfer Handler",()=>{
        frappe.prompt({
    label: 'New Handler',
    fieldname: 'handled_by',
    fieldtype: 'Link',
    options:"Yard Staff"
}, (values) => {
    frappe.confirm('Are you sure you want to proceed?',
    () => {
        frappe.call({
            method:"rental.api.trigger_handler",
            args:{
                booking:frm.doc.name,
                new:values.handled_by
            },
            callback:function(r){
                if(r.message){
                    frappe.msgprint("Done!");
                    frm.reload_doc();
                }
                }
        })
    }, () => {})
})
    })
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
