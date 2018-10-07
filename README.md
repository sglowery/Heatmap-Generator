# Heatmap-Generator
A small Python application to generate heatmaps of test scores from students taking two related tests for
the purpose of looking at trends between the two test scores

# Dependencies
This was made with the Anaconda Python distribution, but all that is needed is matplotlib, numpy and scipy. Written for Python 3.x+

# How to use
heatmap_interface.py is the file you need to run. Data is accepted in either .txt or .csv format, with the structure
of the data looking like this:

```
13,30
1,15
5,20
```

The program will prompt you to choose a file, and while it doesn't matter where it is on your computer, it helps to put
the data in the same folder as the rest of the code.
