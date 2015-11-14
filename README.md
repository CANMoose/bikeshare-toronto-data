# Bike Share Toronto Data Analysis

## Summary

This is a new short project I have been working on where I want to try and datamine some interesting statistics about Bike Share Toronto. One thing I have in mind is to see which stations are most likely to be full or empty and at what times. 

The code to grab and access live data is now running. The script checks the public bike bay XML file every 30 seconds and updates the relevant file in /data. Currently building a dataset and I hope to have data for at least a full week.

bikebay.py contains the code for continulously accessing the live data and writing it to file.
analysis.py will contain code for analyzing the raw data.
