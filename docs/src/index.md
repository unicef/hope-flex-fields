---
title: Documentation
---

hope-flex-fields provides the ability to define a set of fields and related validation rules dynamically. It has been designed as part of the [HOPE](https://github.com/unicef/hct-mis) project to manage user-customizable fields (FlexField). The idea is to have a central business logic repository for data import validation.


It provides four classes:

- [FieldDefinition][hope_flex_fields.models.DataChecker]: This represents a collection of reusable pre-configured fields
- [FlexField][hope_flex_fields.models.FlexField]: Instance like representation of `FieldDefinition` inside a `Fieldset`
- [Fieldset][hope_flex_fields.models.Fieldset]: Group of FlexField
- [DataChecker][hope_flex_fields.models.DataChecker]: Compound of fieldset
