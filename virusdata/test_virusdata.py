from unittest import TestCase
import virusdata


class Test(TestCase):
    def test_get_generators(self):
        self.assertEqual(len(virusdata.get_generators((1, 2))), 3)
        self.assertRaises(ValueError, virusdata.get_generators, (1, 8))

    def test_get_translation_vector_str(self):
        self.assertEqual(virusdata.get_translation_vector_str(virusdata.f), "f")
        self.assertEqual(virusdata.get_translation_vector_str(virusdata.b), "b")
        self.assertEqual(virusdata.get_translation_vector_str(virusdata.s), "s")

    def test_get_single_generator_from_str(self):
        self.assertEqual(virusdata.get_single_generator_from_str("f"), virusdata.f)
        self.assertEqual(virusdata.get_single_generator_from_str("b"), virusdata.b)
        self.assertEqual(virusdata.get_single_generator_from_str("s"), virusdata.s)

        for i in range(1, 56):
            base_vec = virusdata.configs[i][virusdata.BASE_STR]
            self.assertEqual(virusdata.get_single_generator_from_str(i), base_vec)
            self.assertEqual(virusdata.get_single_generator_from_str(str(i)), base_vec)

        self.assertRaises(ValueError, virusdata.get_single_generator_from_str, "garbage_input")
