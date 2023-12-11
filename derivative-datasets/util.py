def find_main_clause_verbs(node):
    return node.xpath(".//w[@role='v' and (@mood='indicative' or @mood='imperative' or @mood='subjunctive' or @mood='infinitive')]")

def is_substantive(node, ancestor):
    """
    Participles that have DetCL as ancestor are substantives,
    but because of deeply nested nominal phrases, we only check up to a specified ancestor
    (i.e., the ancestor that is a sibling of the main clause verb)
    """
    # if node is None:
    #     return False
    if node.attrib.get("rule") == "DetCL":
        return True
    if node == ancestor:
        return False
    return is_substantive(node.getparent(), ancestor)

def find_non_substantive_participles(node):
    """
    Participles are marked by .//w[@mood='participle']
    """
    participles = node.findall(".//w[@mood='participle']")
    if not participles:
        return []
    return [
        ptc for ptc in participles
        if not is_substantive(ptc, node)
    ]

# Let's use the macula TSV to print out verses and highlight backgrounded phrases

# Get the macula TSV
import csv
path_to_macula_tsv = "/home/jcuenod/Programming/symphony-stuff/symphony-backend-atlas-internal/data/Clear-Bible/macula-greek/SBLGNT/tsv/macula-greek-SBLGNT.tsv"
with open(path_to_macula_tsv, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    macula_tsv = list(reader)

# first row is the header
header = macula_tsv[0]

# convert to dictionary list
macula_tsv = [dict(zip(header, row)) for row in macula_tsv[1:]]

# Now we're grouping rows of macula_tsv by ref so we can get a whole verse at a time
macula_tsv_by_ref = {}
for row in macula_tsv:
    ref = row.get("ref").split("!")[0]
    if ref not in macula_tsv_by_ref:
        macula_tsv_by_ref[ref] = []
    macula_tsv_by_ref[ref].append(row)

def get_closest_clause(node):
    if node is None:
        return None
    if node.attrib.get("class") == "cl":
        return node
    return get_closest_clause(node.getparent())

def sort_by_ref(a, b):
    refa = a.attrib.get("ref")
    refb = b.attrib.get("ref")

    # ref is book chapter:verse!word
    bookA, chapterA, verseA, wordA = re.split("[\ :!]", refa)
    bookB, chapterB, verseB, wordB = re.split("[\ :!]", refb)
    if bookA != bookB:
        # books should never be different
        return bookA > bookB
    
    if chapterA != chapterB:
        return int(chapterA) - int(chapterB)
    
    if verseA != verseB:
        return int(verseA) - int(verseB)
    
    return int(wordA) - int(wordB)