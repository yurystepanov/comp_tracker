from django import forms

from .models import make_product_group_spec_queryset


class ProductFilterForm(forms.Form):
    group = None

    def __init__(self, group, is_authenticated=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.group = group

        # add price fields
        field = forms.IntegerField(required=False,
                                   initial=0,
                                   label="Цена от, руб.")
        self.fields['price_from'] = field

        field = forms.IntegerField(required=False,
                                   initial=0,
                                   label="Цена до, руб.")
        self.fields['price_to'] = field

        # add brand field
        field = forms.CharField(required=False,
                                label="Бренд")
        self.fields['brand'] = field

        # add favourites field
        disabled = not is_authenticated
        field = forms.BooleanField(required=False,
                                   label="В избранном",
                                   disabled=disabled,
                                   help_text='(Нужна регистрация)' if disabled else ''
                                   )
        self.fields['favourites'] = field

        # add subscriptions field
        disabled = not is_authenticated
        field = forms.BooleanField(required=False,
                                   label="В рассылке",
                                   disabled=disabled,
                                   help_text='(Нужна регистрация)' if disabled else ''
                                   )
        self.fields['subscriptions'] = field

        # add assembly field
        field = forms.BooleanField(required=False,
                                   label="В сборке")
        self.fields['assembly'] = field

        # add spec fields
        if self.group:
            product_spec = make_product_group_spec_queryset(self.group)

            for [spec, label], filters in product_spec:
                choices = [(item['value'], item['value']) for item in filters]

                field = forms.MultipleChoiceField(required=False,
                                                  choices=choices,
                                                  widget=forms.CheckboxSelectMultiple(),
                                                  label=label
                                                  )

                self.fields[spec] = field
