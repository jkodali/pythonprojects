from django import forms

class GetJobListForm(forms.Form):
    idToSave = forms.DecimalField(max_digits=19, decimal_places=0)