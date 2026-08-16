from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MedicalDevice(models.Model):
    _name = "az.medical.device"
    _description = "Medical Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Device Name", required=True, tracking=True)
    serial_number = fields.Char(string="Serial Number", required=True, copy=False, index=True, tracking=True)
    product_id = fields.Many2one("product.product", string="Product", tracking=True)
    brand = fields.Char(string="Brand", tracking=True)
    model_number = fields.Char(string="Model", tracking=True)
    hospital_id = fields.Many2one(
        "res.partner",
        string="Current Hospital / Customer",
        domain="[('is_hospital', '=', True)]",
        tracking=True,
    )
    purchase_date = fields.Date(string="Purchase / Import Date")
    sale_date = fields.Date(string="Sale Date")
    warranty_end = fields.Date(string="Warranty End Date")
    status = fields.Selection(
        [
            ("in_stock", "In Stock"),
            ("sold", "Sold"),
            ("under_maintenance", "Under Maintenance"),
            ("ready", "Ready for Delivery"),
            ("delivered", "Delivered"),
            ("retired", "Retired"),
        ],
        string="Status",
        default="in_stock",
        required=True,
        tracking=True,
    )
    notes = fields.Text(string="Notes")
    maintenance_ticket_ids = fields.One2many(
        "az.maintenance.ticket", "device_id", string="Maintenance History"
    )
    maintenance_count = fields.Integer(
        string="Maintenance Visits", compute="_compute_maintenance_count"
    )

    _sql_constraints = [
        ("serial_number_unique", "unique(serial_number)", "Serial number must be unique."),
    ]


    @api.depends("maintenance_ticket_ids")
    def _compute_maintenance_count(self):
        for rec in self:
            rec.maintenance_count = len(rec.maintenance_ticket_ids)

    def action_open_maintenance_history(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Maintenance History",
            "res_model": "az.maintenance.ticket",
            "view_mode": "list,form",
            "domain": [("device_id", "=", self.id)],
            "context": {"default_device_id": self.id},
        }
