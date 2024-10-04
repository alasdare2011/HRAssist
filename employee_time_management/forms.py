from django import forms


class TimeOffForm(forms.Form):
    start_date = forms.DateField(label="First Day Away", widget=forms.SelectDateWidget)
    end_date = forms.DateField(label="Last Day Away", widget=forms.SelectDateWidget)
    unpaid_time = forms.FloatField(label="Unpaid time off")
    overtime = forms.FloatField(label="Apply Overtime")

    class Meta:
        fields = ["start_date", "end_date", "unpaid_time"]


class ApplyForOT(forms.Form):
    ot_date = forms.DateField(label="Date", widget=forms.SelectDateWidget)
    hours = forms.FloatField(label="Number of Overtime Hours")

    class Meta:
        fields = ["ot_date", "hours"]
