from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_hospital = fields.Boolean(string="Hospital / Medical Center")
    is_supplier_medical = fields.Boolean(string="Medical Supplier")
