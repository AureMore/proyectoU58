from django.forms.widgets import DateInput

class DateMaskInput(DateInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attrs.update({'data-mask': '99/99/9999'})