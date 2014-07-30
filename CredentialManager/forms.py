from django import forms
from django.core.exceptions import ValidationError
from PPACS import constraint
from Provider.models import Expression


class ExpressionForm(forms.ModelForm):
    class Meta:
        model = Expression

    def clean_variable(self):
        var = self.cleaned_data['variable']

        if var in constraint.ConstraintChecker.RESERVED:
            raise ValidationError('%s is an environment variable, can not use it here' % var)

        return var

    def save(self, user):
        expr = super(ExpressionForm, self).save(commit = False)
        expr.save()
        user.attributes.add(expr)
        user.save()
        return expr