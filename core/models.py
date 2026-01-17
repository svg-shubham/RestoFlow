from django.db import models
from django.conf import settings
from decimal import Decimal


from django.db import models
from django.conf import settings
from decimal import Decimal

class TableSection(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. AC, Family, Rooftop")
    service_charge_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, 
        help_text="Family section ke liye 10.00 likhein"
    )
    is_active = models.BooleanField(default=True, help_text="Kya yeh section abhi operational hai?")
    display_order = models.IntegerField(default=0, help_text="Dashboard par kounsa section pehle dikhega")
    class Meta:
        verbose_name_plural = "Table Sections"
        ordering = ['display_order']

    def __str__(self):
        return self.name


class Table(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'), # FUTURE PROOF: Advance booking ke liye
        ('OUT_OF_ORDER', 'Out of Order'), # FUTURE PROOF: Repair/Cleaning ke liye
    ]
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField(help_text="Kitne log baith sakte hain")
    section = models.ForeignKey(TableSection, on_delete=models.CASCADE, related_name='tables')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    is_active = models.BooleanField(default=True, help_text="Kya yeh table use karne layak hai?")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['table_number']

    def __str__(self):
        return f"T-{self.table_number} ({self.section.name})"

class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    # Food Type choices for icons
    FOOD_TYPE_CHOICES = [
        ('VEG', 'Veg'),
        ('NON_VEG', 'Non-Veg'),
        ('EGG', 'Egg'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, help_text="Ingredients ya dish ki detail")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPE_CHOICES, default='VEG')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True, help_text="Kya ye dish aaj kitchen mein hai?")
    prep_time = models.PositiveIntegerField(default=15, help_text="Minutes mein")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text="GST %")
    is_out_of_stock = models.BooleanField(default=False)
    is_special = models.BooleanField(default=False, verbose_name="Chef's Special")
    @property
    def price_with_tax(self):
        tax_amount = (self.final_price * self.tax_rate) / 100
        return self.final_price + tax_amount

    class Meta:
        ordering = ['category', 'display_order', 'name']

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

# 5. Order (The Main Bill)
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),      # Order liya gaya hai
        ('IN_PROGRESS', 'Kitchen'),  # KOT nikal gayi, khana ban raha hai (Added)
        ('SERVED', 'Served'),        # Khana table par pahunch gaya (Added)
        ('COMPLETED', 'Completed'),  # Bill pay ho gaya aur table khali ho gayi
        ('CANCELLED', 'Cancelled'),
        ('BILLING', 'Billing Request'),
    ]
    PAYMENT_MODE = [
        ('CASH', 'Cash'),
        ('ONLINE', 'Online/UPI'),
        ('CARD', 'Card'),
    ]
    table = models.ForeignKey(Table,on_delete=models.CASCADE,related_name="orders")
    asst_manager = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES, default='PENDING')
    # Financials
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Bina tax ke
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # GST calculation ke liye
    extra_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Final payable

    # Future Proof: Payment tracking
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - Table {self.table.table_number}"
    
class OrderItem(models.Model):
    ITEM_STATUS = [
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready'),
        ('SERVED', 'Served'),
        ('CANCELLED', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ITEM_STATUS, default='PREPARING')

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} (Order #{self.order.id})"

    @property
    def total_price(self):
        return self.quantity * self.price_at_order

