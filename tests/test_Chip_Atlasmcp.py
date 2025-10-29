#!/usr/bin/env python
"""
Unit tests for the Chip_Atlasmcp package.
Run with:
    pytest -v
"""

import os
import pandas as pd
import pytest
from Chip_Atlasmcp import Chip_Atlasmcp


@pytest.fixture(scope="module")
def setup_tmp_results(tmp_path_factory):
    """Fixture to create a temporary directory for saving test results."""
    tmp_dir = tmp_path_factory.mktemp("results")
    os.environ["CHIP_ATLAS_RESULTS_DIR"] = str(tmp_dir)
    return tmp_dir


def test_fetch_and_display_experiment_list(monkeypatch):
    """Test that fetch_and_display returns a DataFrame with expected structure for a known gene."""
    # Patch ensure_metadata_file to skip actual download
    monkeypatch.setattr(
        Chip_Atlasmcp,
        "ensure_metadata_file",
        lambda x, **kwargs: "tests/mock_experiment_list.csv"
    )

    # Create a mock CSV file for testing
    data = {
        "Experimental ID": ["EXP001", "EXP002"],
        "Antigen": ["TP53", "TP53BP1"],
        "Cell type": ["Blood", "Bone"],
        "Genome assembly": ["hg19", "hg38"],
        "Title": ["TP53 ChIP-seq", "TP53BP1 ChIP-seq"]
    }
    df_mock = pd.DataFrame(data)
    df_mock.to_csv("tests/mock_experiment_list.csv", index=False)

    # Run the function
    df = Chip_Atlasmcp.fetch_and_display("experiment_list", "TP53")

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert "Antigen" in df.columns
    assert not df.empty
    assert any(df["Antigen"].str.contains("TP53", case=False))


def test_save_full_dataset_creates_file(setup_tmp_results):
    """Test that save_full_dataset actually creates a CSV file."""
    df = pd.DataFrame({
        "Antigen": ["TP53", "TP53BP1"],
        "Genome assembly": ["hg19", "hg38"]
    })
    Chip_Atlasmcp.save_full_dataset(df, "TP53", "experiment_list")

    results_dir = os.path.expanduser("~/Chip_Atlasmcp/results")
    assert os.path.exists(results_dir), "Results directory not created"

    expected_file = os.path.join(results_dir, "chip_atlas_TP53_experiment_list.csv")
    assert os.path.exists(expected_file), f"Expected file {expected_file} not found"


def test_fetch_and_display_no_data(monkeypatch):
    """Test fetch_and_display when no matching keyword is found."""
    # Patch load_metadata to return dummy dataframe
    dummy_df = pd.DataFrame({
        "Antigen": ["BRCA1", "BRCA2"],
        "Cell type": ["Breast", "Ovary"]
    })
    monkeypatch.setattr(
        Chip_Atlasmcp,
        "load_metadata",
        lambda x, **kwargs: dummy_df
    )

    df = Chip_Atlasmcp.fetch_and_display("analysis_list", "XYZGENE")
    assert df is None or df.empty, "Expected no results for unmatched keyword"


def test_metadata_type_invalid():
    """Ensure that an invalid metadata type returns None."""
    result = Chip_Atlasmcp.ensure_metadata_file("invalid_type")
    assert result is None
