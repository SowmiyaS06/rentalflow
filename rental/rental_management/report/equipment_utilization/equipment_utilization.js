// Copyright (c) 2026, Sowmiya and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Utilization"] = {
    filters: [

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        },

        {
            fieldname: "category",
            label: "Category",
            fieldtype: "Link",
            options: "Equipment Category"
        }

    ],
};
