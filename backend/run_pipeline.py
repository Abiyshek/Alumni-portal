#!/usr/bin/env python3
"""
Main entry point to run the modularized alumni pipeline.
This script imports from the alumni_ml_pipeline package and executes the pipeline.
"""

from alumni_ml_pipeline.main import main

if __name__ == "__main__":
    context, scored_data, scores = main()
    print("\n✓ Pipeline execution completed successfully!")
