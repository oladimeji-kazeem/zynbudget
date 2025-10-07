from django.contrib import admin
from .models import (
    FundType, FundManager, Fund, RSAFund, RSAContribution, RSABalance,
    ManagedFund, ManagedFundTransaction, ManagedFundBalance,
    FundPerformance, FundDataUpload
)


@admin.register(FundType)
class FundTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_system_type', 'is_active']
    list_filter = ['category', 'is_system_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(FundManager)
class FundManagerAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'email', 'phone', 'is_active', 'user']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'email']


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ['name', 'fund_code', 'fund_type', 'fund_manager', 'currency', 'risk_level', 'is_active', 'user']
    list_filter = ['fund_type', 'risk_level', 'is_active', 'currency']
    search_fields = ['name', 'fund_code', 'isin']
    raw_id_fields = ['fund_manager']


@admin.register(RSAFund)
class RSAFundAdmin(admin.ModelAdmin):
    list_display = ['fund', 'rsa_pin', 'pfa_name', 'monthly_salary', 'retirement_age']
    search_fields = ['rsa_pin', 'pfa_name', 'employer_name']
    raw_id_fields = ['fund']


@admin.register(RSAContribution)
class RSAContributionAdmin(admin.ModelAdmin):
    list_display = ['rsa_fund', 'contribution_date', 'contribution_type', 'amount', 'units_purchased', 'nav_per_unit']
    list_filter = ['contribution_type', 'contribution_date']
    search_fields = ['reference_number']
    date_hierarchy = 'contribution_date'


@admin.register(RSABalance)
class RSABalanceAdmin(admin.ModelAdmin):
    list_display = ['rsa_fund', 'balance_date', 'total_contributions', 'market_value', 'cumulative_returns']
    list_filter = ['balance_date']
    date_hierarchy = 'balance_date'


@admin.register(ManagedFund)
class ManagedFundAdmin(admin.ModelAdmin):
    list_display = ['fund', 'investment_strategy', 'minimum_investment', 'distribution_frequency']
    list_filter = ['investment_strategy', 'reinvest_distributions']
    raw_id_fields = ['fund']


@admin.register(ManagedFundTransaction)
class ManagedFundTransactionAdmin(admin.ModelAdmin):
    list_display = ['managed_fund', 'transaction_date', 'transaction_type', 'amount', 'units', 'price_per_unit']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['reference_number']
    date_hierarchy = 'transaction_date'


@admin.register(ManagedFundBalance)
class ManagedFundBalanceAdmin(admin.ModelAdmin):
    list_display = ['managed_fund', 'balance_date', 'total_units', 'market_value', 'total_return_percentage']
    list_filter = ['balance_date']
    date_hierarchy = 'balance_date'


@admin.register(FundPerformance)
class FundPerformanceAdmin(admin.ModelAdmin):
    list_display = ['fund', 'period_type', 'period_end_date', 'period_return_percentage', 'annualized_return_percentage']
    list_filter = ['period_type', 'period_end_date']
    date_hierarchy = 'period_end_date'


@admin.register(FundDataUpload)
class FundDataUploadAdmin(admin.ModelAdmin):
    list_display = ['user', 'upload_type', 'file_name', 'status', 'records_processed', 'uploaded_at']
    list_filter = ['upload_type', 'status', 'uploaded_at']
    search_fields = ['user__username', 'file_name']
    readonly_fields = ['uploaded_at', 'processed_at', 'records_processed', 'records_failed']