from datetime import date

from django import forms

from .models import Experiencia, Visita

CAMPO_TEXTO = 'w-full border border-barrica bg-papel px-3 py-2 rounded-rotulo focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cobre'


class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['nome', 'email', 'telefone', 'experiencia', 'data', 'horario', 'num_pessoas', 'observacoes']
        labels = {
            'nome': 'Nome',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'experiencia': 'Experiência',
            'data': 'Data da visita',
            'horario': 'Horário',
            'num_pessoas': 'Número de pessoas',
            'observacoes': 'Observações',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': CAMPO_TEXTO, 'maxlength': 120, 'required': True}),
            'email': forms.EmailInput(attrs={'class': CAMPO_TEXTO, 'required': True}),
            'telefone': forms.TextInput(attrs={'class': CAMPO_TEXTO, 'maxlength': 20}),
            'experiencia': forms.Select(attrs={'class': CAMPO_TEXTO, 'required': True}),
            'data': forms.DateInput(attrs={'class': CAMPO_TEXTO, 'type': 'date', 'required': True}),
            'horario': forms.TimeInput(attrs={'class': CAMPO_TEXTO, 'type': 'time', 'required': True}),
            'num_pessoas': forms.NumberInput(attrs={'class': CAMPO_TEXTO, 'min': 1, 'required': True}),
            'observacoes': forms.Textarea(attrs={'class': CAMPO_TEXTO, 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['experiencia'].queryset = Experiencia.objects.filter(ativa=True)
        self.fields['data'].widget.attrs['min'] = date.today().isoformat()

    def clean_data(self):
        data = self.cleaned_data['data']
        if data < date.today():
            raise forms.ValidationError('A data da visita não pode ser no passado.')
        return data

    def clean_num_pessoas(self):
        num_pessoas = self.cleaned_data['num_pessoas']
        if num_pessoas < 1:
            raise forms.ValidationError('Informe pelo menos 1 pessoa.')
        return num_pessoas

    def clean_experiencia(self):
        experiencia = self.cleaned_data['experiencia']
        if not experiencia.ativa:
            raise forms.ValidationError('Essa experiência não está mais disponível.')
        return experiencia
