# Al Zahraa Medical Devices — Odoo 19

First working module for Al Zahraa's medical-device workflow.

## Included in v1
- Medical device master record with unique Serial Number
- Device status: in stock / sold / under maintenance / ready / delivered / retired
- Hospital/customer link
- Full maintenance ticket history per device
- Receiving and delivery people on both company and hospital sides
- Fault, diagnosis, technician notes
- Parts/consumables used per maintenance visit
- Estimated and final maintenance cost
- Attachments
- Automatic maintenance ticket numbering
- Chatter/audit trail for tracked changes
- Basic Arabic translation file
- Links to Odoo Sales, Purchases and Stock

## Install
1. Copy the folder `al_zahraa_medical_service` into your Odoo custom addons directory.
2. Restart Odoo.
3. Activate Developer Mode.
4. Apps -> Update Apps List.
5. Search for `Al Zahraa Medical Devices`.
6. Install.

## Target
Built against the Odoo 19.0 module framework.

## Next planned phase
- Dedicated stock screen for new imported devices
- Automatic stock movements for spare parts used in repair
- Repair quotations and invoices
- Printable Arabic maintenance receipt/delivery form
- Dashboard: devices in repair, overdue jobs, hospital history, revenue/cost
- User roles: Admin / Maintenance / Sales / Warehouse
- Warranty alerts
- Barcode/QR lookup by serial number
