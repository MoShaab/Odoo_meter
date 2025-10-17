from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

        # Basic meter fields
    meter_previous = fields.Float(
        string='Previous', 
        digits=(12, 2),
        help='Previous meter reading from last invoice'
        )

    meter_new = fields.Float(
        string='New', 
        digits=(12, 2),
        help='Current meter reading'
        
        )

    meter_actual = fields.Float(
        string='Actual', 
        compute='_compute_meter_actual', 
        store=True, 
        digits=(12, 2),
         help='Calculated consumption'
    )


        # Meter replacement fields
    meter_replaced = fields.Boolean(
        string='Meter Replaced',
        default=False,
        help='Check if meter was replaced during this period'
    )
    old_meter_final_reading = fields.Float(
        string='Old Meter Final Reading',
        digits=(12, 2),
        help='Final reading before meter replacement'
    )

    new_meter_initial_reading = fields.Float(
            string='New Meter Initial Reading',
            digits=(12, 2),
            help='Starting reading of new meter after installation'
        )

            # Visibility control
    show_meter_fields = fields.Boolean(
        compute='_compute_show_meter_fields',
        store=False
    )

    @api.depends('product_id')
    def _compute_show_meter_fields(self):
        """Show meter fields only for metered products."""
        for line in self:
            line.show_meter_fields = line.product_id.is_metered_product if line.product_id else False

    @api.onchange('meter_new', 'meter_previous', 'meter_replaced', 'old_meter_final_reading', 'new_meter_initial_reading')
    def _onchange_meter_readings(self):
        """Calculate actual consumption with meter replacement support."""
        if not self.product_id or not self.product_id.is_metered_product:
            return
        
        if self.meter_replaced:
            # Meter was replaced during period
            # Consumption = (Old meter final - Previous) + (New reading - New meter initial)
            old_consumption = (self.old_meter_final_reading or 0.0) - (self.meter_previous or 0.0)
            new_consumption = (self.meter_new or 0.0) - (self.new_meter_initial_reading or 0.0)
            self.meter_actual = old_consumption + new_consumption
            
            _logger.info(f"Meter replaced - Old consumption: {old_consumption}, New consumption: {new_consumption}, Total: {self.meter_actual}")
        else:
            # Normal calculation
            self.meter_actual = (self.meter_new or 0.0) - (self.meter_previous or 0.0)
        
        # Auto-populate quantity
        if self.meter_actual > 0:
            self.quantity = self.meter_actual

    @api.depends('meter_new', 'meter_previous')
    def _compute_meter_actual(self):
        # Calculate actual consumption.
        for line in self:
            line.meter_actual = (line.meter_new or 0.0) - (line.meter_previous or 0.0)

    @api.onchange('meter_actual')
    def _onchange_meter_actual(self):
        # Auto-populate quantity from actual.
        if self.meter_actual > 0:
            self.quantity = self.meter_actual

    @api.onchange('meter_new', 'meter_previous')
    def _onchange_meter_readings(self):
        # Trigger when readings change.
        self._compute_meter_actual()
        if self.meter_actual > 0:
            self.quantity = self.meter_actual

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # Auto-fill previous reading based on last invoice.
        if self.move_id.partner_id and self.product_id:
            last_line = self.search([
                ('move_id.partner_id', '=', self.move_id.partner_id.id),
                ('move_id.state', '=', 'posted'),
                ('product_id', '=', self.product_id.id),
                ('meter_new', '>', 0)
            ], order='id desc', limit=1)
            if last_line:
                self.meter_previous = last_line.meter_new
