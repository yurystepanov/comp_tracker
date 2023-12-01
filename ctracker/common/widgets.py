from django_filters.widgets import RangeWidget


class DividedRangeWidget(RangeWidget):
    template_name = "widgets/dividedmultiwidget.html"
    use_fieldset = False
    placeholders = ['От', 'До']

    def __init__(self, attrs=None, placeholders=None):
        if placeholders:
            self.placeholders = placeholders
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        for subcontext, placeholder in zip(context["widget"]["subwidgets"], self.placeholders):
            attrs = subcontext['attrs']
            attrs["placeholder"] = placeholder

        return context
