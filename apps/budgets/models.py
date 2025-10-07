from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


# ============================================
# FUND BASE MODELS
# ============================================

class FundType(models.Model):
    """Define different types of funds"""
    CATEGORY_CHOICES = [
        ('RSA', 'RSA Fund'),
        ('MANAGED', 'Managed Fund'),
        ('EQUITY', 'Equity Fund'),
        ('BOND', 'Bond Fund'),
        ('MONEY_MARKET', 'Money Market'),
        ('BALANCED', 'Balanced Fund'),
        ('INDEX', 'Index Fund'),
        ('ETF', 'Exchange Traded Fund'),
        ('MUTUAL', 'Mutual Fund'),
        ('HEDGE', 'Hedge Fund'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fund_types',
        null=True,
        blank=True,
        help_text='Leave blank for system-wide fund types'
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    is_system_type = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fund_types'
        ordering = ['category', 'name']
        verbose_name = 'Fund Type'
        verbose_name_plural = 'Fund Types'
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class FundManager(models.Model):
    """Fund management companies"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fund_managers'
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fund_managers'
        ordering = ['name']
        verbose_name = 'Fund Manager'
        verbose_name_plural = 'Fund Managers'
    
    def __str__(self):
        return self.name


class Fund(models.Model):
    """Base model for all funds"""
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM_LOW', 'Medium-Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('MEDIUM_HIGH', 'Medium-High Risk'),
        ('HIGH', 'High Risk'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='funds'
    )
    fund_type = models.ForeignKey(
        FundType,
        on_delete=models.PROTECT,
        related_name='funds'
    )
    fund_manager = models.ForeignKey(
        FundManager,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_funds'
    )
    
    # Basic Information
    name = models.CharField(max_length=200)
    fund_code = models.CharField(max_length=50, blank=True)
    isin = models.CharField(max_length=12, blank=True, help_text='International Securities Identification Number')
    
    # Fund Details
    inception_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True)
    
    # Fees
    management_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Annual management fee %'
    )
    performance_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Performance fee %'
    )
    entry_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Entry/Purchase fee %'
    )
    exit_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Exit/Redemption fee %'
    )
    
    # Additional Information
    description = models.TextField(blank=True)
    investment_objective = models.TextField(blank=True)
    benchmark = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'funds'
        ordering = ['name']
        verbose_name = 'Fund'
        verbose_name_plural = 'Funds'
    
    def __str__(self):
        return f"{self.name} ({self.fund_code})"


# ============================================
# RSA FUND MODELS
# ============================================

class RSAFund(models.Model):
    """RSA (Retirement Savings Account) Fund specific data"""
    CONTRIBUTION_TYPE_CHOICES = [
        ('EMPLOYEE', 'Employee Contribution'),
        ('EMPLOYER', 'Employer Contribution'),
        ('VOLUNTARY', 'Voluntary Contribution'),
        ('TRANSFER', 'Transfer In'),
    ]
    
    fund = models.OneToOneField(
        Fund,
        on_delete=models.CASCADE,
        related_name='rsa_details',
        primary_key=True
    )
    
    # RSA Specific Fields
    rsa_pin = models.CharField(max_length=50, blank=True, help_text='RSA PIN Number')
    pfa_name = models.CharField(max_length=200, blank=True, help_text='Pension Fund Administrator')
    pfa_code = models.CharField(max_length=50, blank=True)
    
    # Contribution Rates
    employee_contribution_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8.00,
        help_text='Employee contribution %'
    )
    employer_contribution_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text='Employer contribution %'
    )
    
    # Employment Information
    employer_name = models.CharField(max_length=200, blank=True)
    monthly_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Retirement Information
    retirement_age = models.IntegerField(default=60)
    expected_retirement_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rsa_funds'
        verbose_name = 'RSA Fund'
        verbose_name_plural = 'RSA Funds'
    
    def __str__(self):
        return f"RSA: {self.fund.name}"


class RSAContribution(models.Model):
    """Track RSA contributions"""
    CONTRIBUTION_TYPE_CHOICES = [
        ('EMPLOYEE', 'Employee Contribution'),
        ('EMPLOYER', 'Employer Contribution'),
        ('VOLUNTARY', 'Voluntary Contribution'),
        ('TRANSFER', 'Transfer In'),
    ]
    
    rsa_fund = models.ForeignKey(
        RSAFund,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    
    contribution_date = models.DateField()
    contribution_type = models.CharField(max_length=20, choices=CONTRIBUTION_TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Units and NAV
    units_purchased = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0
    )
    nav_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        help_text='Net Asset Value per unit'
    )
    
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rsa_contributions'
        ordering = ['-contribution_date']
        verbose_name = 'RSA Contribution'
        verbose_name_plural = 'RSA Contributions'
    
    def __str__(self):
        return f"{self.contribution_date} - {self.get_contribution_type_display()} - {self.amount}"


class RSABalance(models.Model):
    """Track RSA fund balances over time"""
    rsa_fund = models.ForeignKey(
        RSAFund,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    
    balance_date = models.DateField()
    
    # Contribution Breakdown
    total_employee_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_employer_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_voluntary_contributions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Investment Performance
    total_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    nav_per_unit = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Returns
    investment_returns = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cumulative_returns = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Fees
    management_fees_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rsa_balances'
        ordering = ['-balance_date']
        unique_together = ['rsa_fund', 'balance_date']
        verbose_name = 'RSA Balance'
        verbose_name_plural = 'RSA Balances'
    
    def __str__(self):
        return f"{self.rsa_fund.fund.name} - {self.balance_date}"
    
    @property
    def total_contributions(self):
        return (
            self.total_employee_contributions +
            self.total_employer_contributions +
            self.total_voluntary_contributions
        )


# ============================================
# MANAGED FUND MODELS
# ============================================

class ManagedFund(models.Model):
    """Managed Fund specific data"""
    INVESTMENT_STRATEGY_CHOICES = [
        ('GROWTH', 'Growth'),
        ('VALUE', 'Value'),
        ('INCOME', 'Income'),
        ('BALANCED', 'Balanced'),
        ('AGGRESSIVE', 'Aggressive'),
        ('CONSERVATIVE', 'Conservative'),
        ('INDEX', 'Index/Passive'),
    ]
    
    fund = models.OneToOneField(
        Fund,
        on_delete=models.CASCADE,
        related_name='managed_details',
        primary_key=True
    )
    
    # Investment Strategy
    investment_strategy = models.CharField(
        max_length=20,
        choices=INVESTMENT_STRATEGY_CHOICES,
        blank=True
    )
    
    # Asset Allocation (Target percentages)
    target_equity_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Target % in equities'
    )
    target_bonds_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Target % in bonds'
    )
    target_cash_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Target % in cash/money market'
    )
    target_alternatives_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Target % in alternatives'
    )
    
    # Fund Characteristics
    minimum_investment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    minimum_additional_investment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Distribution
    distribution_frequency = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g., Quarterly, Semi-Annual, Annual'
    )
    reinvest_distributions = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'managed_funds'
        verbose_name = 'Managed Fund'
        verbose_name_plural = 'Managed Funds'
    
    def __str__(self):
        return f"Managed: {self.fund.name}"


class ManagedFundTransaction(models.Model):
    """Track managed fund transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('PURCHASE', 'Purchase'),
        ('REDEMPTION', 'Redemption'),
        ('SWITCH_IN', 'Switch In'),
        ('SWITCH_OUT', 'Switch Out'),
        ('DIVIDEND', 'Dividend'),
        ('CAPITAL_GAIN', 'Capital Gain'),
        ('FEE', 'Fee'),
    ]
    
    managed_fund = models.ForeignKey(
        ManagedFund,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # Transaction Details
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Transaction amount (positive for inflow, negative for outflow)'
    )
    units = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        help_text='Number of units transacted'
    )
    price_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        help_text='Price/NAV per unit'
    )
    
    # Fees
    fees_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'managed_fund_transactions'
        ordering = ['-transaction_date']
        verbose_name = 'Managed Fund Transaction'
        verbose_name_plural = 'Managed Fund Transactions'
    
    def __str__(self):
        return f"{self.transaction_date} - {self.get_transaction_type_display()} - {self.amount}"


class ManagedFundBalance(models.Model):
    """Track managed fund balances over time"""
    managed_fund = models.ForeignKey(
        ManagedFund,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    
    balance_date = models.DateField()
    
    # Holdings
    total_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    nav_per_unit = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Cost Basis
    total_invested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Total amount invested (excluding fees)'
    )
    total_fees_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Performance
    unrealized_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    realized_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_dividends_received = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Asset Allocation (Actual percentages)
    actual_equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    actual_bonds_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    actual_cash_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    actual_alternatives_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'managed_fund_balances'
        ordering = ['-balance_date']
        unique_together = ['managed_fund', 'balance_date']
        verbose_name = 'Managed Fund Balance'
        verbose_name_plural = 'Managed Fund Balances'
    
    def __str__(self):
        return f"{self.managed_fund.fund.name} - {self.balance_date}"
    
    @property
    def total_return(self):
        return self.unrealized_gain_loss + self.realized_gain_loss + self.total_dividends_received
    
    @property
    def total_return_percentage(self):
        if self.total_invested > 0:
            return (self.total_return / self.total_invested) * 100
        return Decimal('0.00')


# ============================================
# PERFORMANCE TRACKING
# ============================================

class FundPerformance(models.Model):
    """Track fund performance metrics over time"""
    PERIOD_TYPE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name='performance_records'
    )
    
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    period_start_date = models.DateField()
    period_end_date = models.DateField()
    
    # NAV Values
    opening_nav = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    closing_nav = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    high_nav = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    low_nav = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    
    # Returns
    period_return_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Return for this period %'
    )
    ytd_return_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Year-to-date return %'
    )
    annualized_return_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Annualized return %'
    )
    
    # Risk Metrics
    volatility = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Standard deviation of returns'
    )
    sharpe_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Risk-adjusted return'
    )
    
    # Benchmark Comparison
    benchmark_return_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0
    )
    alpha = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Excess return vs benchmark'
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fund_performance'
        ordering = ['-period_end_date']
        unique_together = ['fund', 'period_type', 'period_start_date', 'period_end_date']
        verbose_name = 'Fund Performance'
        verbose_name_plural = 'Fund Performance Records'
    
    def __str__(self):
        return f"{self.fund.name} - {self.period_type} - {self.period_end_date}"


# ============================================
# BULK UPLOAD TRACKING
# ============================================

class FundDataUpload(models.Model):
    """Track bulk fund data uploads"""
    UPLOAD_TYPE_CHOICES = [
        ('RSA_CONTRIBUTIONS', 'RSA Contributions'),
        ('RSA_BALANCES', 'RSA Balances'),
        ('MANAGED_TRANSACTIONS', 'Managed Fund Transactions'),
        ('MANAGED_BALANCES', 'Managed Fund Balances'),
        ('FUND_PERFORMANCE', 'Fund Performance'),
        ('NAV_UPDATES', 'NAV Updates'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fund_uploads'
    )
    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name='uploads',
        null=True,
        blank=True
    )
    
    upload_type = models.CharField(max_length=30, choices=UPLOAD_TYPE_CHOICES)
    file = models.FileField(upload_to='fund_data/%Y/%m/')
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    records_processed = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'fund_data_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'Fund Data Upload'
        verbose_name_plural = 'Fund Data Uploads'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_upload_type_display()} - {self.uploaded_at.strftime('%Y-%m-%d')}"