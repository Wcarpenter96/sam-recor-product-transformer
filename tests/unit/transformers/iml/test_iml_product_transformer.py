import copy
import json
import os
from unittest import TestCase

from recor_product_transformer.libs.transformers.iml.iml_product_transformer import (
    ImlProductTransformer,
)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files")


class TestImlProductTransformer(TestCase):

    def test_transform_product(self):
        with open(os.path.join(SAMPLE_DATA_DIR, "test_product_1.json"), "r") as fp:
            test_product_1 = json.loads(fp.read())

        test_transformer = ImlProductTransformer()
        raw_json = test_transformer.transform(test_product_1)

        expected_json = copy.deepcopy(test_product_1)
        self.assertEqual(expected_json, raw_json)
