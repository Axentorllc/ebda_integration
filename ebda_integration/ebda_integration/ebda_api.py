import frappe
import requests
from dataclasses import dataclass
from frappe.model.document import Document
from ebda_integration.ebda_integration.utils import *

@dataclass
class EbdaAPI:
    settings: Document = frappe.get_single("Ebda Integration Settings")
    username: str = settings.get("username")
    password: str = settings.get_password("password", False)
    base_url: str = settings.get("base_url")
    api_endpoint: str = settings.get("api_endpoint")
    check_session_url: str = "/api/post/v2/check_session"
    login: str = "/api/post/v2/login"


    def auth(self):
        url = self.base_url + self.login
        try:
            data = {
                "username": self.username,
    			"password": self.password,
			}
            response = requests.post(url=url, json=data, verify=False)
            response.raise_for_status()  # Raises HTTPError for non-200 status codes
            response = response.json()
            if response.get("status_code") == 200:
                frappe.db.set_value(self.settings.doctype, self.settings.doctype, "token", response.get("token"))
                frappe.db.commit()
            return response

        except requests.exceptions.RequestException as e:
            frappe.log_error(title="Ebda Integration Auth", message=frappe.get_traceback())
            frappe.throw(f"An error occurred: {e}")
            return None
        
    def check_session(self):
        "params: token | return (status_code, message)"
        url = self.base_url + self.check_session_url
        data = frappe._dict({"token": self.settings.get_password("token", False)})
        try:
            response = requests.post(url, json=data, verify=False)
            response.raise_for_status()  # Raises HTTPError for non-200 status codes
            response = response.json()
            if response.get("status_code") == 200 and response.get("message") == "Token is active":
                return True
            return False
        except requests.exceptions.RequestException as e:
            frappe.log_error(title="Check Session", message=frappe.get_traceback())
            frappe.throw(f"An error occurred: {e}")
            return None
        
    def check_token(self):
        if self.check_session():
            return True
        else:
            return self.auth()
        
    def get_support_types(self):
        url = self.base_url + self.api_endpoint + "support-types"
        try:
            self.check_token()
            response = requests.post(url, json={"token": self.settings.get_password("token", False)}, verify=False)
            response.raise_for_status()  # Raises HTTPError for non-200 status codes
            return response.json()


        except requests.exceptions.RequestException as e:
            frappe.log_error(title="Get Support Types", message=frappe.get_traceback())
            frappe.throw(f"An error occurred: {e}")
            return None

    def get_surveys_for_support_type(self, params: dict):
        url = self.base_url + self.api_endpoint + "surveys"
        try:
            self.check_token()
            params.update({"token": self.settings.get_password("token", False)})
            response = requests.post(
                url, json=params, verify=False)
            response.raise_for_status()
            return response.json().get("surveys")

        except requests.exceptions.RequestException as e:
            frappe.log_error(
                title="Get Surveys For Support Type", message=frappe.get_traceback()
            )
            frappe.throw(f"An error occurred: {e}")
            return None

@frappe.whitelist()
def _auth():
    EbdaAPI().auth()

@frappe.whitelist()
def _refresh_token():
    EbdaAPI().check_token()
    
@frappe.whitelist()
def get_surveys():
    ebda = EbdaAPI()
    if not ebda.settings.get("enabled"):
        help_msg(ebda.settings.doctype)

    support_types = ebda.get_support_types()
    if support_types:
        update_support_types(support_types.get("support_types", []))

    support_type_list = build_params_for_support_types()
    for params in support_type_list:
        if (
            params.get("support_type_id")
            and params.get("date_from")
            and params.get("date_to")
        ):
            support_type_id = params.pop("name")
            surveys = ebda.get_surveys_for_support_type(params)
            answers = get_answers_from(surveys)

            if answers:
                create_ebda_survey_from(answers, support_type_id)


@frappe.whitelist()
def get_odoo_support_types():
    ebda = EbdaAPI()

    if not ebda.settings.get("enabled"):
        help_msg(ebda.settings.doctype)
        

    support_types = ebda.get_support_types()
    if support_types:
        update_support_types(support_types.get("support_types", []))


def help_msg(doctype: str):
    msg = f"<span class='text-muted'>Please enable the integration from <b>{doctype}</b> Doctype</span>"
    frappe.throw(msg=f"Ebda Integration is disabled <br><hr>{msg}")
