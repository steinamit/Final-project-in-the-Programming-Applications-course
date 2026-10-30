# Folder Analysis Tool

A desktop app that scans a folder recursively, shows it as a tree with sizes, and charts the distribution of file sizes.

**Context:** final project (task 3), Programming Applications, M.Sc. · **Team:** Eden Shmuel, Amit Stein, Oria Shapira

## Features
- Enter a folder path and scan it recursively.
- **Tree view:** folders and files with size in MB and share of the parent folder.
- **Statistics:** total size and a chart of file counts by size range (1 KB to 100 MB+).
- Error message for an invalid path.

## Structure
`Task_3.py` holds two classes: `DirectoryScanner` (recursive scan and size data) and `TreeApp` (Tkinter interface with an embedded chart). `מטלה 3.docx` documents the algorithm and design.

**Tools:** Python · Tkinter · pandas · seaborn · matplotlib
