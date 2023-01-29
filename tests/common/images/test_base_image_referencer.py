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

    def test_localhost_image_name(self):
        self.assertFalse(self.run_is_valid_public_image_valid('localhost:320000/video-conferencing-ms-example'))

    def test_valid_image_name(self):
        self.assertTrue(self.run_is_valid_public_image_valid('node:16'))

    def test_valid_image_name_2(self):
        self.assertTrue(self.run_is_valid_public_image_valid('ubuntu'))
