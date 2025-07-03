from django.test import TestCase

from testutils.factories import FieldDefinitionFactory, FieldsetFactory

from hope_flex_fields.models import DataChecker, DataCheckerFieldset, FlexField


class TestGroupFunctionality(TestCase):
    def setUp(self):
        self.field_def = FieldDefinitionFactory()

        self.documents_fieldset = FieldsetFactory(name="Documents", default_group="documents")
        self.personal_fieldset = FieldsetFactory(name="Personal", default_group="personal")
        self.root_fieldset = FieldsetFactory(name="Root", default_group="")

        self.doc_field = FlexField.objects.create(
            name="document_name", definition=self.field_def, fieldset=self.documents_fieldset
        )
        self.personal_field = FlexField.objects.create(
            name="first_name", definition=self.field_def, fieldset=self.personal_fieldset
        )
        self.root_field = FlexField.objects.create(name="id", definition=self.field_def, fieldset=self.root_fieldset)

        self.datachecker = DataChecker.objects.create(name="TestChecker")

    def test_fieldset_default_group(self):
        self.assertEqual(self.documents_fieldset.default_group, "documents")
        self.assertEqual(self.personal_fieldset.default_group, "personal")
        self.assertEqual(self.root_fieldset.default_group, "")

    def test_datachecker_fieldset_override_fields(self):
        dc_fieldset = DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.documents_fieldset,
            override_default_value=True,
            override_group="custom_docs",
        )

        self.assertTrue(dc_fieldset.override_default_value)
        self.assertEqual(dc_fieldset.override_group, "custom_docs")

    def test_get_fields_with_groups_no_override(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker, fieldset=self.documents_fieldset, override_default_value=False
        )

        fields_with_groups = list(self.datachecker.get_fields_with_groups())
        self.assertEqual(len(fields_with_groups), 1)

        fs, field, group = fields_with_groups[0]
        self.assertEqual(group, "documents")  # Should use fieldset's default_group

    def test_get_fields_with_groups_with_override(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.documents_fieldset,
            override_default_value=True,
            override_group="custom_group",
        )

        fields_with_groups = list(self.datachecker.get_fields_with_groups())
        self.assertEqual(len(fields_with_groups), 1)

        fs, field, group = fields_with_groups[0]
        self.assertEqual(group, "custom_group")  # Should use override_group

    def test_get_fields_with_groups_override_empty(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker, fieldset=self.documents_fieldset, override_default_value=True, override_group=""
        )

        fields_with_groups = list(self.datachecker.get_fields_with_groups())
        self.assertEqual(len(fields_with_groups), 1)

        fs, field, group = fields_with_groups[0]
        self.assertEqual(group, "")  # Should be empty string when override_group is empty

    def test_process_data_with_groups(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker, fieldset=self.documents_fieldset, override_default_value=False
        )
        DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.personal_fieldset,
            override_default_value=True,
            override_group="custom_personal",
        )
        DataCheckerFieldset.objects.create(
            checker=self.datachecker, fieldset=self.root_fieldset, override_default_value=False
        )

        input_data = {"document_name": "test_doc.pdf", "first_name": "John", "id": "12345"}

        processed_data = self.datachecker.process_data_with_groups(input_data)

        self.assertIn("documents", processed_data)
        self.assertIn("custom_personal", processed_data)
        self.assertIn("id", processed_data)  # Root level

        self.assertEqual(processed_data["documents"]["document_name"], "test_doc.pdf")
        self.assertEqual(processed_data["custom_personal"]["first_name"], "John")
        self.assertEqual(processed_data["id"], "12345")

    def test_process_data_with_groups_empty_group(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker, fieldset=self.documents_fieldset, override_default_value=True, override_group=""
        )

        input_data = {"document_name": "test_doc.pdf"}
        processed_data = self.datachecker.process_data_with_groups(input_data)

        # Should be at root level
        self.assertIn("document_name", processed_data)
        self.assertEqual(processed_data["document_name"], "test_doc.pdf")

    def test_process_data_with_groups_prefix_with_placeholder(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.documents_fieldset,
            override_default_value=False,
            prefix="doc_%s_",
        )

        input_data = {"doc_document_name_": "test_doc.pdf"}
        processed_data = self.datachecker.process_data_with_groups(input_data)

        self.assertIn("documents", processed_data)
        self.assertEqual(processed_data["documents"]["document_name"], "test_doc.pdf")

    def test_process_data_with_groups_prefix_without_placeholder(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.documents_fieldset,
            override_default_value=False,
            prefix="doc_",
        )

        input_data = {"doc_document_name": "test_doc.pdf"}
        processed_data = self.datachecker.process_data_with_groups(input_data)

        self.assertIn("documents", processed_data)
        self.assertEqual(processed_data["documents"]["document_name"], "test_doc.pdf")

    def test_process_data_with_groups_field_not_in_data(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.documents_fieldset,
            override_default_value=False,
        )

        input_data = {"other_field": "some_value"}
        processed_data = self.datachecker.process_data_with_groups(input_data)

        # Should not contain the field since it's not in input data
        self.assertNotIn("documents", processed_data)
        self.assertEqual(processed_data, {})

    def test_process_data_with_groups_multiple_fields_same_group(self):
        DataCheckerFieldset.objects.create(
            checker=self.datachecker,
            fieldset=self.documents_fieldset,
            override_default_value=False,
        )

        # Create another field in the same fieldset
        FlexField.objects.create(
            name="document_type", definition=self.field_def, fieldset=self.documents_fieldset
        )

        input_data = {"document_name": "test_doc.pdf", "document_type": "PDF"}
        processed_data = self.datachecker.process_data_with_groups(input_data)

        self.assertIn("documents", processed_data)
        self.assertEqual(processed_data["documents"]["document_name"], "test_doc.pdf")
        self.assertEqual(processed_data["documents"]["document_type"], "PDF")
