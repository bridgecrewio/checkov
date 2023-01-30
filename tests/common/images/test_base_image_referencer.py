import unittest


class TestImageReferencerBase(unittest.TestCase):
    # noinspection PyMethodMayBeStatic
    def run_is_valid_public_image_valid(self, image_name: str) -> bool:
        from checkov.common.images.image_referencer import is_valid_public_image_name
        return is_valid_public_image_name(image_name)

    def test_invalid_image_name_replace(self):
        self.assertFalse(self.run_is_valid_public_image_valid('registry-auth.twistlock.com/tw_<REPLACE_TWISTLOCK_TOKEN>/twistlock/console:console_20_04_163'))

    def test_invalid_image_name_extraction(self):
        self.assertFalse(self.run_is_valid_public_image_valid(
            "gcr.io/[\"${{'develop': {'project_id': 'develop'}, 'production': {'project_id': 'production'}}[\"var.env\"].project_id}\"]/notifier:aa123aa"
        ))

    def test_invalid_image_name_var_reference(self):
        self.assertFalse(self.run_is_valid_public_image_valid('gcr.io/example/base:$IMAGE_TAG'))

    def test_localhost_image_name(self):
        self.assertFalse(self.run_is_valid_public_image_valid('localhost:320000/video-conferencing-ms-example'))

    def test_cname_with_port_image_name(self):
        self.assertFalse(self.run_is_valid_public_image_valid('example.local:5004/video-conferencing-ms-example:1.2.3'))

    def test_valid_image_name(self):
        self.assertTrue(self.run_is_valid_public_image_valid('node:16'))

    def test_valid_image_name_2(self):
        self.assertTrue(self.run_is_valid_public_image_valid('ubuntu'))

    def test_valid_image_name_3(self):
        self.assertTrue(self.run_is_valid_public_image_valid('gcr.io/develop/notifier:aa123aa'))
