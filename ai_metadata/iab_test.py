import unittest
import iab
import pandas as pd


class TaxonomyTest(unittest.TestCase):

  def test_to_list_returns_list_of_names(self):
    names = ["name1", "name2", "name3"]
    df = pd.DataFrame({"Unique ID": ["0", "1", "2"], "Name": names})
    taxonomy = iab.Taxonomy("test", df)

    self.assertEqual(taxonomy.tolist(), names)

  def test_get_entities(self):
    names = ["name1", "name2", "name3"]
    df = pd.DataFrame({"Unique ID": ["0", "1", "2"], "Name": names})
    taxonomy = iab.Taxonomy("test", df)

    self.assertEqual(
        taxonomy.get_entities(),
        [
            iab.TaxonomyEntity(
                taxonomy_name="test", unique_id="0", name="name1"
            ),
            iab.TaxonomyEntity(
                taxonomy_name="test", unique_id="1", name="name2"
            ),
            iab.TaxonomyEntity(
                taxonomy_name="test", unique_id="2", name="name3"
            ),
        ],
    )

  def test_get_entities_by_name(self):
    names = ["name1", "name2", "name3"]
    df = pd.DataFrame({"Unique ID": ["0", "1", "2"], "Name": names})
    taxonomy = iab.Taxonomy("test", df)

    self.assertEqual(
        taxonomy.get_entities_by_name(["name2"]),
        [
            iab.TaxonomyEntity(
                taxonomy_name="test", unique_id="1", name="name2"
            ),
        ],
    )
