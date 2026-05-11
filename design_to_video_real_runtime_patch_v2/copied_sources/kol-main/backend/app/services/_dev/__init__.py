"""app/services/_dev — dev-only adapters and helpers.

.. warning::
    This package must NEVER be imported in production code paths.
    All classes here are gated behind ``is_production_or_staging()`` checks.
"""
