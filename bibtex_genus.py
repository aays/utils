'''
bibtex parser that fixes genus/species names and other junk

usage - python bibtex_genus.py [infile] [outfile]

first - make sure there are no instances of 'month' in the bibtex entries - this breaks the parser.
(the bug seems to be on bibtexparser's end)

can fix with grep -v 'month' file.bib > new_file.bib

TODO:
- add functionality that takes in a file w/ a list of species names, instead of hardcoding them here
- convert sys.argv inputs to argparse
'''

import bibtexparser
import sys
import re

fname = sys.argv[-2]
outname = sys.argv[-1]
max_authors = 10 # add an argparse thing for this later

with open(fname) as f:
    try:
        bib_database = bibtexparser.load(f)
    except KeyError:
        print('Error: Please remove the "month" field from your BibTeX file.')
        print('This can be done using grep -v "month" file.bib > new_file.bib.')
        sys.exit(0)

genus_names = [
    'chlamydomonas', 'drosophila',
    'saccharomyces', 'arabidopsis', 'caenorhabditis', 'mus']

species_names = [
    'reinhardtii', 'simulans', 'melanogaster',
    'persimilis', 'cerevisiae', 'paradoxus', 'pombe',
    'thaliana', 'elegans', 'musculus', 'reinhardi']

counts = dict.fromkeys(['entry_count', 'genus_only_count', 'genus_species_count', 'abbr_genus_species_count', 'max_authors_count'], 0)

def fix_authors(bib_entry_author, max_authors):
    '''(str, int) -> str, bool
    Will edit author field if author count > predefined max authors.
    Returns modified author value and bool representing whether a change was made.
    Bool used to increment dict keeping count if necessary.
    '''
    author_count = bib_entry['author'].count('and') + 1
    if author_count < max_authors: 
        return bib_entry['author'], False # no changes needed
    elif author_count >= max_authors:
        author_split = bib_entry['author'].split(' ')
        and_locations = [i for i in range(len(author_split)) if author_split == 'and']
        assert len(and_locations) >= max_authors
        final_and = and_locations[:9][-1]
        authors_trunc = ' '.join(author_split[: final_and]) + ' and others'
        return authors_trunc, True

for entry in bib_database.entries:
    counts['entry_count'] += 1
    # fix author counts if too many
    entry['author'], author_changes = fix_authors(entry, max_authors = max_authors)
    counts['max_authors_count'] += author_changes # increment count if authors modified
    # edit title for genus/species name
    entry['title'] = entry['title'].replace('\n', ' ') # remove newline chars
    entry['title'] = re.sub('[Dd][Nn][Aa]', '{DNA}', entry['title']) # make sure 'DNA' is in all caps
    for genus in genus_names:
        if genus in entry['title'].lower():
            genus_index = entry['title'].lower().find(genus) # first check there isn't already a {}
            if entry['title'][genus_index - 1] == '{':
                continue
            else:
                title_split = entry['title'].split(' ')
                for i in range(len(title_split)):
                    if title_split[i].lower() == genus: # genus matched
                        if i == len(title_split) - 1: # only genus - at end of paper name
                            title_split[i] = '{' + title_split[i].title() + '}'
                            counts['genus_only_count'] += 1
                            continue
                        elif not i == len(title_split) - 1 and title_split[i + 1] in species_names: # title contains genus AND species
                            title_split[i] = '{' + title_split[i].title()
                            title_split[i + 1] = title_split[i + 1].lower() + '}'
                            counts['genus_species_count'] += 1
                        else: # only genus name, not at end
                            title_split[i] = '{' + title_split[i].title() + '}'
                            counts['genus_only_count'] += 1
                    else:
                        continue
    for species in species_names: # if genus abbreviated - 'D. melanogaster'
        if species in entry['title'].lower():
            species_index = entry['title'].lower().find(species) # check there isn't already a {}
            if entry['title'][species_index + len(species)] == '}': # there's already a }
                continue
            else:
                title_split = entry['title'].split(' ')
                if not set(title_split).intersection(set(genus_names)): # genus name not present
                    if entry['title'][species_index - 2] == '.': # genus is abbreviated
                        for i in range(len(title_split)):
                            if title_split[i - 1].lower().endswith('.') and title_split[i].lower() == species:
                                title_split[i - 1] = '{' + title_split[i - 1].title()
                                title_split[i] = title_split[i].lower() + '}'
                                counts['abbr_genus_species_count'] += 1

with open(outname, 'w') as outfile:
    bibtexparser.dump(bib_database, outfile)

print('Parsing complete.')
print(counts['entry_count'], 'entries parsed.')
print(counts['genus_species_count'], 'genus-species combinations corrected.')
print(counts['genus_only_count'], 'genus-only titles corrected.')
print(counts['abbr_genus_species_count'], 'genus-species (w/ abbreviated genus) combinations corrected.')
print(counts['max_authors_count'], 'author lists exceeded max_authors =', max_authors, 'and were truncated.) 
