frappe.ui.form.on('Sales Invoice', {
    customer(frm) {
    	frappe.call({
		method: "erpnext.accounts.utils.get_balance_on",
		args: {date: frm.doc.posting_date, party_type: 'Customer', party: frm.doc.customer},
		callback: function(r) {
			frm.set_value("total_debit",r.message)
		}
	})
    }
})
