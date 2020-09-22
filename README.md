# About
This is a program to scrape a number of UK retailers selling the new RTX 3000 series GPUs from Nvidia

# Setup
- Setup the venv
- Install requirements with pip
- Insert a Discord webhook url into `config.json`
- Create the sqlite db with tables as shown below
- run the scripts.

# DB schema
```
CREATE TABLE scan (
    row_id INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL,
    price INTEGER NOT NULL,
    availability TEXT NOT NULL,
    time INTEGER NOT NULL
);
```
