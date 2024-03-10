frappe.listview_settings["Ebda Survey"] = {
	onload: function (listview) {
		listview.page.add_button(__("Get Surveys"), function () {
			frappe.call({
				method: "ebda_integration.ebda_integration.ebda_api.get_surveys",
				freeze: true,
				freeze_message: "Getting Surveys..",
				callback: function(r) {
					if(!r.exc) {
						frappe.show_alert({message: "Getting Surveys successfully.", indicator:"green"})
					}
				}
			})
		}).addClass("btn btn-primary")
	}
};