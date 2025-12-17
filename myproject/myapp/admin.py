from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Product, ProductHistory, DailyToken


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("name", "price", "stock")
    show_change_link = True


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "user_link", "product_count")
    list_display_links = ("id", "first_name", "last_name")
    search_fields = ("first_name", "last_name", "email", "user__username")
    list_filter = ("user",)
    inlines = [ProductInline]

    def user_link(self, obj):
        if obj.user_id:
            url = f"/admin/auth/user/{obj.user_id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"

    user_link.short_description = "User"

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "customer_link")
    list_display_links = ("id", "name")
    search_fields = ("name", "description", "customer__first_name", "customer__last_name", "customer__email")
    list_filter = ("customer",)
    autocomplete_fields = ("customer",)
    fieldsets = (
        (None, {
            "fields": ("name", "description")
        }),
        ("Inventory & Pricing", {
            "fields": ("price", "stock")
        }),
        ("Relations", {
            "fields": ("customer",)
        })
    )

    def customer_link(self, obj):
        if obj.customer_id:
            url = f"/admin/myapp/customer/{obj.customer_id}/change/"
            return format_html('<a href="{}">{} {}</a>', url, obj.customer.first_name, obj.customer.last_name)
        return "-"

    customer_link.short_description = "Customer"


class ProductHistoryInline(admin.TabularInline):
    model = ProductHistory
    extra = 0
    readonly_fields = ("purchase_date",)
    autocomplete_fields = ("product",)


@admin.register(ProductHistory)
class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_link", "product_link", "purchase_date")
    list_display_links = ("id",)
    search_fields = (
        "customer__first_name",
        "customer__last_name",
        "customer__email",
        "product__name",
    )
    list_filter = ("purchase_date", "customer", "product")
    readonly_fields = ("purchase_date",)
    autocomplete_fields = ("customer", "product")

    def customer_link(self, obj):
        url = f"/admin/myapp/customer/{obj.customer_id}/change/"
        return format_html('<a href="{}">{} {}</a>', url, obj.customer.first_name, obj.customer.last_name)

    customer_link.short_description = "Customer"

    def product_link(self, obj):
        url = f"/admin/myapp/product/{obj.product_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.product.name)

    product_link.short_description = "Product"


@admin.register(DailyToken)
class DailyTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user_link", "date_created_short")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("date_created",)
    autocomplete_fields = ("user",)

    def user_link(self, obj):
        url = f"/admin/auth/user/{obj.user_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    user_link.short_description = "User"

    def date_created_short(self, obj):
        return obj.date_created.strftime("%Y-%m-%d") if obj.date_created else "-"

    date_created_short.short_description = "Date Created"