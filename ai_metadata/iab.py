"""Handles custom taxonomy creation and adds support for IAB."""

import dataclasses
from typing import Iterable
import pandas as pd


_CONTENT_TAXONOMY_URL = "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/main/Content%20Taxonomies/Content%20Taxonomy%202.2.tsv"

_AUDIENCE_TAXONOMY_URL = "https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/refs/heads/main/Audience%20Taxonomies/Audience%20Taxonomy%201.1.tsv"


@dataclasses.dataclass
class TaxonomyEntity:
  taxonomy_name: str
  unique_id: str
  name: str


class Taxonomy:
  """Represents a classification system.

  Supports classification entities with unique IDs and names.
  """

  def __init__(
      self,
      name: str,
      df: pd.DataFrame,
      id_col: str = "Unique ID",
      name_col: str = "Name",
  ):
    self._name = name
    self._taxonomy_df = df
    self._id_col = id_col
    self._name_col = name_col

  def tolist(self) -> list[str]:
    """Returns a list of all the names in the taxonomy."""
    return self._taxonomy_df[self._name_col].tolist()

  def get_entities(self) -> list[TaxonomyEntity]:
    """Returns all of the entities in the Taxonomy."""
    return [
        TaxonomyEntity(
            taxonomy_name=self._name,
            unique_id=row[self._id_col],
            name=row[self._name_col],
        )
        for _, row in self._taxonomy_df.iterrows()
    ]

  def get_entities_by_name(self, names: Iterable[str]) -> list[TaxonomyEntity]:
    """Gets a list of entities based on their names.

    Args:
      names: The names for which to return the entity instances.

    Returns:
      A list of the corresponding entities in the input list. Invalid, or names
      that do not exist in the taxonomy are ignored.
    """
    filtered_df = self._taxonomy_df[
        self._taxonomy_df[self._name_col].isin(names)
    ]
    return [
        TaxonomyEntity(
            taxonomy_name=self._name,
            unique_id=row[self._id_col],
            name=row[self._name_col],
        )
        for _, row in filtered_df.iterrows()
    ]


def create_content_taxonomy() -> Taxonomy:
  """Creates a Taxonomy representing the IAB Content Taxonomy 2.2."""
  df_taxonomy = pd.read_csv(_CONTENT_TAXONOMY_URL, sep="\t", header=1)
  return Taxonomy("IAB_CONTENT_2_2", df_taxonomy.astype(str))


def create_audience_taxonomy() -> Taxonomy:
  """Creates a Taxonomy representing the IAB Audience Taxonomy 1.1."""
  df_taxonomy = pd.read_csv(_AUDIENCE_TAXONOMY_URL, sep="\t")
  df_taxonomy = df_taxonomy.rename(
      columns={"Condensed Name (1st, 2nd, Last Tier)": "Name"}
  )
  return Taxonomy("IAB_AUDIENCE_1_1", df_taxonomy.astype(str))
