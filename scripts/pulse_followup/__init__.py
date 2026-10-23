"""Exploratory existing-data pulse follow-up (plan .agents/plans/2026-10-23-pulse-followup-parallel.md).

Separate from the closed primacy procedure (scripts/ddm/primacy.py, amendment 6 item 8). Every analysis here is
exploratory. Package A (data.py, config.py, io.py) freezes the shared trial table and analysis contract that
packages B-G read; they must not redefine trial sets, strata or censoring.
"""
