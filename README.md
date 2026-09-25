### C3:In README_internals.md: rename a test Yard Staff record. Does handled_by on linked Rental Bookings update automatically? Why or why not?
    Yes, Renaming a record in `Yard Staff` will also be updated automatically in the linked field 'handled_by' which is in `Rental Bookings`.
    Because remaming a record will trigger frapperename_doc() method with merge=False which is responsible for this automatic update.

### E1:Call self.save() inside on_update to "recompute" final_amount and observe what breaks. Explain and correct the pattern in README_internals.md.
    Calling self.save() inside an on_update lifecycle method to recompute the final amount causes "RecursionError: maximum recursion depth exceeded". 
    The self.save() method triggers the on_update function, again the on_update function triggers self.save() which is inside on_update and this continues...
    def on_update():
        self.save()
            ->def on_update():
                 self.save()
                    ->this goes on
    Hence, to avoid this recursion pitfall calculating the final amount inside validate function is enough no need to call self.save() method.

### E2:Call frappe.rename_doc("Yard Staff", old, new, merge=False) and show linked fields update automatically. Explain when merge=True would be dangerous.
    sowmiya@SOWMIYA:~/new-bench$ bench --site rental.local console
    Apps in this namespace:
    frappe, rental
    In [1]: frappe.rename_doc("Yard Staff","STAFF-0003", "STAFF-0005", merge=False)
    Out[1]: 'STAFF-0005'

    'merge=True' would be dangerous because the separate datas in records "STAFF-0003" and "STAFF-0005" both could merge and the records will get collapsed

### E3:In the Equipment Unit controller's on_update, which pattern would you use and why?
### doc = frappe.get_doc("RentFlow Settings", "RentFlow Settings")
### threshold = doc.low_availability_threshold
### threshold = frappe.db.get_value("RentFlow Settings", None, "low_availability_threshold")
    
    (1)doc = frappe.get_doc("RentFlow Settings", "RentFlow Settings")
    threshold = doc.low_availability_threshold
    Here,we only need the field 'low_availability_threshold' but the whole doctype is retrieved
    (2)threshold = frappe.db.get_value("RentFlow Settings", None, "low_availability_threshold")
    Here,the field 'low_availability_threshold' only is needed and the field is only retrieved

    So, in both the cases the field 'low_availability_threshold' is only required so the best pattern is (2).

### H1:In README_internals.md: why does a frappe.call inside the validate client event not work, and why must async availability checks happen in onload/refresh instead?
    frappe.call function works asynchronously as it has a callback function waiting for a response
    frappe.call({
        method:"abc.xyz",
        callback(r):function{

        }
    })
    But validate function in client event runs synchronously as it is a lifecycle event triggered automatically.So frappe.call inside the validate client event 
    does not work. 
    Onload/refresh event runs whenever the doctype which will be helpful for checking stuffs whenever a document loads

### D2:Don't leak data" task: two versions of a whitelisted method returning booking data — unsafe (all fields to any caller) and safe (frappe.get_list, strips customer_phone/customer_email for non-Manager callers).
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

### B3 — Dangerous Patterns
### document lifecycle bugs
### The snippet below has two bugs related to document lifecycle. Identify both and write the corrected version in README_internals.md:
### def validate(self):
###     self.rental_total = sum(r.line_amount for r in self.items)
###     self.save()
###     unit = frappe.get_doc("Equipment Unit", self.items[0].equipment_unit)
###     unit.current_status = "Rented"
###     unit.save()
    Calling self.save() inside validate function again triggers the lifecycle method validate() which causes an infinite recursion

### J:In README_internals.md: explain frappe.get_all() inside the Jinja template directly vs. pre-computing in before_print() and referencing doc.precomputed_field.
    If you use this print format, Jinja will reach the database every single time for every single document and this can causes severe lag over serve.Use before_print() for any logic involving loops, calculations,etc., this lessens the server waiting time as well.Hence direct calculataion using jinja can be used for simple logics only.

### K2: Spot the N+1 Identify and rewrite:
# N+1 PROBLEM - fix this
# bookings = frappe.get_all("Rental Booking", fields=["name","handled_by"])
# for b in bookings:
#    staff = frappe.get_doc("Yard Staff", b.handled_by)
#    print(staff.staff_name, staff.phone)
    The N+1 query problem in the code happens because frappe.get_doc runs a separate database query inside a loop for every single booking.
    Therefore,If we have 100 bookings.. script will hit the database 101 times 
        => 1 to get bookings + 100 to get each staff member's details

### N1: List every use of ignore_permissions=True; justify each in one sentence. Add a JS field hide on customer_phone for non-managers, then show a direct API call can still retrieve it. Explain why hiding a field in JavaScript is not a security measure
    Ignore permission provides access to a particular doctype to the user to even if they aren't given access to that particular doctype.  Hiding the data from UI doesn't mean they aren't available in database so to avoid this we have to set perm level for that field and same permission level to the user only then we can prevent the visibility to that field even through API call



