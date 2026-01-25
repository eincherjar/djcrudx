from django.core.paginator import Paginator
from django.shortcuts import render
from django.apps import apps
from django.conf import settings


def render_with_readonly(request, template_name, context, readonly_fields=None):
    """Render with automatic readonly fields application"""
    if readonly_fields and "form" in context:
        form = context["form"]
        if hasattr(form, "instance") and form.instance and form.instance.pk:
            apply_readonly_fields(form, readonly_fields)
            context["readonly_fields"] = readonly_fields

    return render(request, template_name, context)


def apply_readonly_fields(form, readonly_fields):
    """Apply readonly to form fields"""
    for field_name in readonly_fields:
        if field_name in form.fields:
            form.fields[field_name].widget.attrs["readonly"] = True

    # Remove locked fields from cleaned_data to prevent modification
    original_clean = form.clean

    def clean_with_readonly():
        cleaned_data = original_clean()
        # Remove all readonly fields if form is bound to existing object
        if hasattr(form, "instance") and form.instance.pk:
            for field_name in readonly_fields:
                cleaned_data.pop(field_name, None)
        return cleaned_data

    form.clean = clean_with_readonly
    return readonly_fields


class PaginationMixin:
    """Mixin for easy pagination in views"""

    def paginate_queryset(self, queryset, request, per_page_default=25):
        """
        Paginate queryset and return page_obj and context for pagination component

        Args:
            queryset: QuerySet to paginate
            request: HttpRequest object
            per_page_default: default number of items per page

        Returns:
            tuple: (page_obj, pagination_context)
        """
        per_page = int(request.GET.get("per_page", per_page_default))
        paginator = Paginator(queryset, per_page)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        pagination_context = {
            "page_obj": page_obj,
            "request_get": request.GET,
            "per_page_options": [10, 25, 50, 100],
            "current_per_page": per_page,
            "start_index": page_obj.start_index() if page_obj.object_list else 0,
            "end_index": page_obj.end_index() if page_obj.object_list else 0,
            "total_count": paginator.count,
            "base_url": f"{request.path}?",
            "per_page_base_url": f"{request.path}?",
        }

        return page_obj, pagination_context


class DataTableMixin:
    """Mixin for datatable handling"""

    def prepare_datatable(self, table_config, page_obj):
        """
        Generate datatable data from configuration

        Args:
            table_config: list of dictionaries with column configuration
            page_obj: pagination object

        Returns:
            tuple: (table_headers, table_rows)
        """
        table_headers = []
        for col in table_config:
            header = {"label": col["label"], "filter_field": col.get("filter_field"), "field": col.get("field"), "key": col.get("key")}
            table_headers.append(header)

        table_rows = []
        for obj in page_obj.object_list:
            row = []
            for col in table_config:
                cell_value = col["value"](obj)

                # If cell has URL, create link
                if col.get("url"):
                    url_data = col["url"](obj)
                    if isinstance(url_data, tuple) and len(url_data) == 2:
                        # Format: ("app:name", {"arg": value})
                        from django.urls import reverse

                        url_name, url_kwargs = url_data
                        url = reverse(url_name, kwargs=url_kwargs)
                    else:
                        # Fallback for string URL
                        url = str(url_data)
                    cell_value = f'<a href="{url}" class="text-blue-600 hover:text-blue-800">{cell_value}</a>'

                # If cell has actions, add action icons
                if col.get("actions"):
                    actions_html = ""
                    for action in col["actions"]:
                        action_url_data = action["url"](obj)
                        if isinstance(action_url_data, tuple) and len(action_url_data) == 2:
                            from django.urls import reverse

                            action_url = reverse(action_url_data[0], kwargs=action_url_data[1])
                        else:
                            action_url = str(action_url_data)
                        action_title = action.get("title", "")
                        actions_html += f'<a href="{action_url}" class="mr-1 text-gray-600 hover:text-gray-800" title="{action_title}">{action["icon"]}</a>'
                    cell_value = f"{actions_html}{cell_value}"

                # If cell has is_badge flag, pass it to template
                if col.get("is_badge"):
                    if col.get("badge_data"):
                        # Handle badge_data for multiple badges
                        badges = col["badge_data"](obj)
                        badge_html = ""
                        for badge in badges:
                            # Check if color starts with [ (custom) or is Tailwind class
                            bg_class = f"bg-{badge['background_color']}" if not badge["background_color"].startswith("[") else f"bg-{badge['background_color']}"
                            text_class = f"text-{badge['text_color']}" if not badge["text_color"].startswith("[") else f"text-{badge['text_color']}"
                            badge_html += f'<span class="px-2 py-1 rounded text-xs {bg_class} {text_class}">{badge["name"]}</span>'
                        cell_value = badge_html
                    elif hasattr(cell_value, "bg_color"):
                        # Handle single badge with attributes
                        cell_value.is_badge = True

                row.append(cell_value)
            table_rows.append(row)

        return table_headers, table_rows


class ReadonlyFormMixin:
    """Mixin for automatic readonly fields application"""

    readonly_fields = []

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(self, "object") and self.object and self.readonly_fields:
            apply_readonly_fields(form, self.readonly_fields)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.readonly_fields:
            context["readonly_fields"] = self.readonly_fields
        return context


class CrudListMixin(PaginationMixin, DataTableMixin):
    """Complete mixin for list views with datatable and personalization"""

    def apply_user_view(self, table_config, request, view_name):
        """Apply user's personalized view - requires TableView model in your app"""
        # This method requires a TableView model in your application
        # Remove or customize this method based on your needs
        return table_config

    def get_datatable_context(self, queryset, filter_instance, table_config, request, view_name=None):
        """
        Complete datatable handling - filtering, pagination, data generation

        Args:
            queryset: QuerySet to display
            filter_instance: django-filter instance
            table_config: column configuration
            request: HttpRequest object
            view_name: view name for personalization

        Returns:
            dict: context for template
        """
        # Temporarily disabled - apply user's personalized view
        # if view_name and (request.GET.get('view') or TableView.objects.filter(user=request.user, view_name=view_name, is_default=True).exists()):
        #     table_config = self.apply_user_view(table_config, request, view_name)

        # Handle sorting
        ordering = request.GET.get("ordering")
        if ordering:
            # Check if field exists in table_config
            valid_fields = [col.get("field") for col in table_config if col.get("field")]
            field = ordering.lstrip("-")
            if field in valid_fields:
                queryset = queryset.order_by(ordering)

        # Pagination
        page_obj, pagination_context = self.paginate_queryset(queryset, request)

        # Generate datatable
        table_headers, table_rows = self.prepare_datatable(table_config, page_obj)

        context = {
            "filter": filter_instance,
            "headers": table_headers,
            "rows": table_rows,
            **pagination_context,
        }
        
        # Dodaj base_template tylko jeśli nie został już ustawiony
        if "base_template" not in context:
            context["base_template"] = getattr(settings, 'DJCRUDX_BASE_TEMPLATE', None)

        # Add data for column configuration
        if view_name:
            context["view_name"] = view_name
            context["all_columns"] = [{"key": col.get("key") or col.get("field") or col["label"], "label": col["label"]} for col in table_config]

        return context
