# Examples

## Validate json

Let imagine a simple datastructure like:


    data = [
        {"name" : "John",   "last_name": "Doe", "gender": "M"},
        {"name" : "Jane",   "last_name": "Doe", "gender": "F"},
        {"name" : "Andrea", "last_name": "Doe", "gender": "X"},
        {"name" : "Mary",   "last_name": "Doe", "gender": "1"}
    ]


Let start creating validation rules (here in the code, you can use the admin interface otherwise)
    
    
        fs, __ = Fieldset.objects.get_or_create(name="test.xlsx")
    
        charfield = FieldDefinition.objects.get(field_type=forms.CharField)
        choicefield = FieldDefinition.objects.get(field_type=forms.ChoiceField)
    
        FlexField.objects.get_or_create(name="name", fieldset=fs, field=charfield)
        FlexField.objects.get_or_create(name="last_name", fieldset=fs, field=charfield)
        FlexField.objects.get_or_create(name="gender", fieldset=fs, field=choicefield,
                                        attrs={"choices": [["M", "M"], ["F", "F"], ["X", "X"]})

Validate the file against it

        errors = fs(data)
        print(errors)

```python
{4: {'gender': ['Select a valid choice. 1 is not one of the available choices.']}}

```

## Detect unknown data

With the example above just uses

      errors = fs.validate(data, fail_if_alien=True)
      print(errors)

```python
{
    1: {'-': ["Alien values found {'unknown'}"]},
    4: {'gender': ['Select a valid choice. 1 is not one of the available choices.']}
}
```
