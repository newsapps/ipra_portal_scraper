ipra_portal_scraper
===================

Scrape cases, subjects, media item and document metadata from http://portal.iprachicago.org/

Assumptions
-----------

* Python 2.7 (though I don't see any reason this wouldn't work with Python 3.4+)
* virtualenvwrapper

Installation
------------

Clone the repository:

    git clone https://github.com/newsapps/ipra_portal_scraper.git

Create a virtualenv for this project:

    mkvirtualenv ipra_portal_scraper

Install dependencies:

    pip install -r requirements.txt

Scraping the portal
-------------------

    ./scrape.py > cases.json

Export only the subjects from the scraped JSON
----------------------------------------------

    cat cases.json | ./export_subjects_table.py > subjects.csv


Authors
-------

* Geoff Hing <geoffhing@gmail.com> for the Chicago Tribune DataViz team
