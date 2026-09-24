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





































### Rental Management

Rental Management

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app rental
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/rental
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
