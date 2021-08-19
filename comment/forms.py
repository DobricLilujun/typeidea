from django import forms

from .models import Comment


# forms.ModelForm 表格填写中需要 填写 meta中 fields
class CommentForm(forms.ModelForm):
    nickname = forms.CharField(
        label="nickname",
        max_length=50,
        widget=forms.widgets.Input(
            attrs={'class': 'form-control col-sm-4'}
        )
    )
    email = forms.CharField(
        label='Email',
        max_length=50,
        widget=forms.widgets.EmailInput(
            attrs={'class': 'form-control col-sm-4'}
        )
    )
    website = forms.CharField(
        label='website',
        max_length=100,
        widget=forms.widgets.URLInput(
            attrs={'class': 'form-control col-sm-4'}
        )
    )
    content = forms.CharField(
        label='content',
        max_length=2000,
        widget=forms.widgets.Textarea(
            attrs={'rows': 6, 'cols': 60, 'class': 'form-control col-sm-12'}
        )
    )

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError('内容长度不能如此短!')
        return content

    class Meta:
        model = Comment
        fields = {'content','nickname','email','website'}
