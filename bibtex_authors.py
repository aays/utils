'''
bibtex parser that shrinks author counts

usage - python bibtex_authors.py [infile] [outfile]

first - make sure there are no instances of 'month' in the bibtex entries - this breaks the parser.
(the bug seems to be on bibtexparser's end)

can fix with grep -v 'month' file.bib > new_file.bib

TODO:
- convert sys.argv inputs to argparse
- add option for nauthors
'''

import bibtexparser
import sys
import re

def fix_authors(bib_entry, max_authors):
    '''(str, int) -> str, bool
    Will edit author field if author count > predefined max authors.
    Returns modified author value and bool representing whether a change was made.
    Bool used to increment dict keeping count if necessary.
    '''
    author_count = bib_entry['author'].replace('\n', ' ').count(' and ') + 1
    if author_count < max_authors: 
        return bib_entry['author'], False # no changes needed
    elif author_count >= max_authors:
        author_split = bib_entry['author'].replace('\n', ' ').split(' ')
        and_locations = [i for i in range(len(author_split)) if author_split[i] == 'and']
        try:
            assert len(and_locations) + 1 >= max_authors
        except:
            print(author_count, bib_entry['author'], author_split, len(and_locations), '\n')
        final_and = and_locations[:9][-1]
        authors_trunc = ' '.join(author_split[: final_and]) + ' and others'
        return authors_trunc, True

def main(bib_database):
    print('started')
    for entry in bib_database.entries:
        if 'author' not in entry.keys(): # books etc w/o author records
            continue
        counts['total_count'] += 1
        entry['author'], changed = fix_authors(entry, max_authors = max_authors)
        if changed:
            counts['changed_count'] += 1
        elif not changed:
            counts['unchanged_count'] += 1
    return bib_database

if __name__ == '__main__':
    fname = sys.argv[-2]
    outname = sys.argv[-1]
    max_authors = 10 

    counts = dict.fromkeys(['total_count', 'changed_count', 'unchanged_count'], 0)

    with open(fname) as f:
        try:
            bib_database = bibtexparser.load(f)
        except KeyError:
            print('Error: Please remove the "month" field from your BibTeX file.')
            print('This can be done using grep -v "month" file.bib > new_file.bib.')
            sys.exit(0)
    out_database = main(bib_database = bib_database)
    with open(outname, 'w') as outfile:
        bibtexparser.dump(out_database, outfile)

    print('Parsing complete.')
    print(counts['total_count'], 'entries parsed.')
    print(counts['changed_count'], 'entries altered.')
    print(counts['unchanged_count'], 'entries did not need alteration.')
