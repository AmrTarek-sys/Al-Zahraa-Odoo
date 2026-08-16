from odoo import api, fields, models


class MaintenanceTicket(models.Model):
    _name = "az.maintenance.ticket"
    _description = "Device Maintenance Ticket"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "received_date desc, id desc"

    name = fields.Char(
        string="Ticket Number",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
    )
    device_id = fields.Many2one(
        "az.medical.device",
        string="Device",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    serial_number = fields.Char(
        related="device_id.serial_number",
        string="Serial Number",
        store=True,
        readonly=True,
    )
    hospital_id = fields.Many2one(
        "res.partner",
        string="Hospital / Customer",
        domain="[('is_hospital', '=', True)]",
        required=True,
        tracking=True,
    )
    received_date = fields.Datetime(
        string="Received Date",
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    issue_description = fields.Text(string="Reported Fault", required=True, tracking=True)
    inspection_result = fields.Text(string="Inspection / Diagnosis")
    technician_notes = fields.Text(string="Technician Notes")
    status = fields.Selection(
        [
            ("received", "Received"),
            ("inspection", "Under Inspection"),
            ("repair", "Under Repair"),
            ("waiting_parts", "Waiting for Parts"),
            ("ready", "Ready for Delivery"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="received",
        required=True,
        tracking=True,
    )
    warranty_status = fields.Selection(
        [
            ("in_warranty", "In Warranty"),
            ("out_of_warranty", "Out of Warranty"),
            ("unknown", "Unknown"),
        ],
        string="Warranty Status",
        default="unknown",
        tracking=True,
    )
    company_received_by = fields.Many2one(
        "res.users", string="Received by Company Employee", tracking=True
    )
    hospital_delivered_by = fields.Char(
        string="Delivered by Hospital Representative", tracking=True
    )
    company_delivered_by = fields.Many2one(
        "res.users", string="Delivered by Company Employee", tracking=True
    )
    hospital_received_by = fields.Char(
        string="Received by Hospital Representative", tracking=True
    )
    delivery_date = fields.Datetime(string="Delivery Date", tracking=True)
    parts_line_ids = fields.One2many(
        "az.maintenance.part", "ticket_id", string="Parts / Consumables Used"
    )
    estimated_cost = fields.Monetary(string="Estimated Cost", currency_field="currency_id")
    final_cost = fields.Monetary(string="Final Cost", currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    notes = fields.Text(string="Internal Notes")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("az.maintenance.ticket") or "New"
        records = super().create(vals_list)
        for rec in records:
            rec.device_id.write({
                "status": "under_maintenance",
                "hospital_id": rec.hospital_id.id,
            })
        return records

    def write(self, vals):
        res = super().write(vals)
        if "status" in vals:
            for rec in self:
                if rec.status == "ready":
                    rec.device_id.status = "ready"
                elif rec.status == "delivered":
                    rec.device_id.status = "delivered"
                    if not rec.delivery_date:
                        rec.delivery_date = fields.Datetime.now()
                elif rec.status in ("received", "inspection", "repair", "waiting_parts"):
                    rec.device_id.status = "under_maintenance"
        return res

    def action_start_inspection(self):
        self.write({"status": "inspection"})

    def action_start_repair(self):
        self.write({"status": "repair"})

    def action_ready(self):
        self.write({"status": "ready"})

    def action_deliver(self):
        self.write({
            "status": "delivered",
            "delivery_date": fields.Datetime.now(),
        })


class MaintenancePart(models.Model):
    _name = "az.maintenance.part"
    _description = "Maintenance Part / Consumable"

    ticket_id = fields.Many2one(
        "az.maintenance.ticket", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one("product.product", string="Part / Consumable", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)
    unit_price = fields.Float(string="Unit Cost")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
