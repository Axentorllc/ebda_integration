// Copyright (c) 2024,  Axentor LLC and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ebda Integration Settings', {
	refresh: function(frm) {
		frm.add_custom_button("Auth", function (frm) {
			frappe.call({
				method: "ebda_integration.ebda_integration.ebda_api._auth",
				freeze: true,
				freeze_message: __("Please Wait ..."),
				callback: (r) => {
						// on success
						if (!r.exe) {
							frm.reload_doc();
							frappe.show_alert({message:__("Authenticated Successfully"), indicator:"green"});
						}
			
					},
			})
		}, "Actions")

		frm.add_custom_button("Refresh Token", function (frm) {
			frappe.call({
				method: "ebda_integration.ebda_integration.ebda_api._refresh_token",
				freeze: true,
				freeze_message: __("Please Wait ..."),
				callback: (r) => {
						// on success
						if (!r.exe) {
							frm.reload_doc();
							frappe.show_alert({message:__("Token Refreshed Successfully"), indicator:"green"});
						}
			
					},
			})
		}, "Actions")
	}
});
