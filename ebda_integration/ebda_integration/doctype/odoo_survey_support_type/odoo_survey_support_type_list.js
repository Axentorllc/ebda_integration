frappe.listview_settings["Odoo Survey Support Type"] = {
	onload: function (listview) {
		listview.page.add_button(__("Get Support Types"), function () {
			frappe.call({
				method: "ebda_integration.ebda_integration.ebda_api.get_odoo_support_types",
				freeze: true,
				freeze_message: "Getting Support Types..",
				callback: function(r) {
					if(!r.exc) {
						frappe.msgprint({message: "Please make sure to set the <b>Last Synced Survey</b> datetime for newly added Support types", indicator:"green"})
					}
				}
			})
		}).addClass("btn btn-primary")
	}
};