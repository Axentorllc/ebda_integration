import frappe
from frappe.utils import now_datetime, cstr


def build_params_for_support_types():
    support_types = frappe.get_all(
        "Odoo Survey Support Type",
        fields=["name", "odoo_id", "text", "last_synced_survey"],
    )
    params = []
    for support_type in support_types:
        params.append(
            {
                "name": support_type.get("name"),
                "support_type_id": support_type.get("odoo_id"),
                "date_from": support_type.get("last_synced_survey"),
                "date_to": now_datetime(),
            }
        )
    return params


def update_support_types(support_types: list):
    for st in support_types:
        if not frappe.db.exists("Odoo Survey Support Type", {"odoo_id": st.get("id")}):
            frappe.get_doc(
                {
                    "doctype": "Odoo Survey Support Type",
                    "odoo_id": st.get("id"),
                    "text": st.get("text"),
                }
            ).insert(ignore_permissions=True)


def get_answers_from(survays: list = []) -> list:
    answers = []

    for survey in survays:
        record = {
            "id": survey.get("id"),
            "support_type_id": survey.get("support_type_id"),
            "code": survey.get("code"),
            "trouble_id": survey.get("trouble_id"),
            "industrial_activity_id": survey.get("industrial_activity_id"),
            "gov_id": survey.get("gov_id"),
            "area_id": survey.get("area_id"),
            "answers": [],
        }

        for answer in survey.get("answer_ids", []):
            filtered_answer = {key: value for key, value in answer.items() if value}

            if filtered_answer and not any(
                key.startswith("answer") for key in filtered_answer
            ):
                filtered_answer.update({"answer_boolean": answer.get("answer_boolean")})

            record["answers"].append(update_answer_key_value(filtered_answer))
        answers.append(record)

    return answers


def update_answer_key_value(dictionary):
    for key in dictionary:
        if key.startswith("answer"):
            dictionary.update({"answer_text": dictionary.pop(key), "answer_type": key})
            return dictionary
    return dictionary


def create_ebda_survey_from(answers: list, support_type_id: str):

    for answer in answers:
        create_ebda_survey(
            id=answer.get("id"),
            support_type_id=answer.get("support_type_id"),
            trouble_id=answer.get("trouble_id"),
            industrial_activity_id=answer.get("industrial_activity_id"),
            gov_id=answer.get("gov_id"),
            area_id=answer.get("area_id"),
            survey_answers=answer.get("answers"),
        )
        frappe.db.set_value(
            "Odoo Survey Support Type",
            support_type_id,
            "last_synced_survey",
            now_datetime(),
        )


def create_ebda_survey(
    id,
    support_type_id,
    trouble_id,
    industrial_activity_id,
    gov_id,
    area_id,
    survey_answers,
):

    if not frappe.db.exists("Ebda Survey", {"id": id}):
        ebda_survey = frappe.get_doc(
            {
                "doctype": "Ebda Survey",
                "id": id,
                "support_type_id": cstr(support_type_id),
                "trouble_id": cstr(trouble_id),
                "industrial_activity_id": cstr(industrial_activity_id),
                "gov_id": gov_id,
                "area_id": area_id,
                "survey_answers": survey_answers,
            }
        )
        ebda_survey.insert(ignore_mandatory=True)
        return ebda_survey.get("name")
    return None
