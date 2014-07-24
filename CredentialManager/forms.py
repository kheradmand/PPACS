from django import forms
from Provider.models import Expression


class ExpressionForm(forms.ModelForm):
    class Meta:
        model = Expression
    def save(self, user):
        expr = super(ExpressionForm, self).save(commit = False)
        expr.save()
        user.attributes.add(expr)
        user.save()
        return expr