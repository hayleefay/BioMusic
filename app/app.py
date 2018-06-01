from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from itertools import chain
import collections

app = Flask(__name__)

# declaring dictionaries for note/key/tempo hashing
NOTE_FREQ = {'G_1': 196.00, 'G#_1': 207.65, 'A_1': 220.00, 'A#_1': 233.08,
             'B_1': 246.94, 'C_1': 261.63, 'C#_1': 277.18, 'D_1': 293.66,
             'D#_1': 311.13, 'E_1': 329.63, 'F_1': 349.23, 'F#_1': 369.99,
             'G_2': 392.00, 'G#_2': 415.30, 'A_2': 440.00, 'A#_2': 466.16,
             'B_2': 493.88, 'C_2': 523.25, 'C#_2': 554.37, 'D_2': 587.33,
             'D#_2': 622.25, 'E_2': 659.25, 'F_2': 698.46, 'F#_2': 739.99,
             'G_3': 783.99, 'G#_3': 830.61, 'A_3': 880.00, 'A#_3': 932.33,
             'B_3': 987.77}

SHEET_NOTES = {196.00: 'G,', 207.65: 'G,', 220.00: 'A,', 233.08: 'A,',
               246.94: 'B,', 261.63: 'C', 277.18: 'C', 293.66: 'D',
               311.13: 'D', 329.63: 'E', 349.23: 'F', 369.99: 'F',
               392.00: 'G', 415.30: 'G', 440.00: 'A', 466.16: 'A',
               493.88: 'B', 523.25: 'c', 554.37: 'c', 587.33: 'd',
               622.25: 'd', 659.25: 'e', 698.46: 'f', 739.99: 'f',
               783.99: 'g', 830.61: 'g', 880.00: 'a', 932.33: 'a',
               987.77: 'b'}

NOTE_LIST = list(NOTE_FREQ.keys())

C_MAJOR = ['G_1', 'A_1', 'B_1', 'C_1', 'D_1', 'E_1', 'F_1', 'G_2', 'A_2', 'B_2', 'C_2', 'D_2', 'E_2', 'F_2', 'G_3', 'A_3', 'B_3']
G_MAJOR = ['G_1', 'A_1', 'B_1', 'C_1', 'D_1', 'E_1', 'F#_1', 'G_2', 'A_2', 'B_2', 'C_2', 'D_2', 'E_2', 'F#_2', 'G_3', 'A_3', 'B_3']
D_MAJOR = ['G_1', 'A_1', 'B_1', 'C#_1', 'D_1', 'E_1', 'F#_1', 'G_2', 'A_2', 'B_2', 'C#_2', 'D_2', 'E_2', 'F#_2', 'G_3', 'A_3', 'B_3']
D_MINOR = ['G_1', 'A_1', 'A#_1', 'C_1', 'D_1', 'E_1', 'F_1', 'G_2', 'A_2', 'A#_2', 'C_2', 'D_2', 'E_2', 'F_2', 'G_3', 'A_3', 'A#_3']
G_MINOR = ['G_1', 'A_1', 'A#_1', 'C_1', 'D_1', 'D#_1', 'F_1', 'G_2', 'A_2', 'A#_2', 'C_2', 'D_2', 'D#_2', 'F_2', 'G_3', 'A_3', 'A#_3']

KEYS = {'Cmaj': C_MAJOR, 'Gmaj': G_MAJOR, 'Dmaj': D_MAJOR, 'Dmin': D_MINOR, 'Gmin': G_MINOR}
KEY_LIST = ['Cmaj', 'Gmaj', 'Dmaj', 'Dmin', 'Gmin']
TEMPOS = [120, 250, 400, 600]


def get_chord(note, key_list):
    '''
    Used when protein is within conserved domain. Takes in note and key and
    returns list of two harmonious notes.
    Inputs: note- name of current note
            key_list- the key that the piece of music will be in
    Outputs: list of two harmonious notes to be included in final music
    '''
    i = key_list.index(note)

    # small hashing to add variability, depending on index, harmony
    # intervals will be different
    if i % 2 == 0:
        i1 = 2
        i2 = 4
    else:
        i1 = 3
        i2 = 5
    try:
        # if note is not close to top of scale
        note1 = NOTE_FREQ[key_list[i + i1]]
        note2 = NOTE_FREQ[key_list[i + i2]]
    except:
        # if note is too close to top, take intervals below
        note1 = NOTE_FREQ[key_list[i - i1]]
        note2 = NOTE_FREQ[key_list[i - i2]]

    return [note1, note2]


def map_protein(protein, regions):
    '''
    Function to take in protein and return musical features
    Inputs: protein- string containing the amino acids in protein sequence
            regions- list of lists wihch comprise the conserved domains in
                     specific protein
    Outputs: key- string specifying the key of music
             tempo- integer specifying tempo of music
             notes- list of lists containing hertz value for each note
             duration- list of duration of notes
    '''
    all_reg = []
    # combine all coding regions into one list
    for reg in regions:
        all_reg.append(list(range(reg[0], reg[1] + 1)))
    all_reg = list(chain(*all_reg))

    # retrieve first few amino acids to determine tempo and key
    start = protein[:10]

    t = [ord(x) for x in start[:5]]
    k = [ord(x) for x in start[5:]]

    tempo = TEMPOS[sum(t) % len(TEMPOS)]
    key = KEY_LIST[sum(k) % len(KEY_LIST)]

    # count occurances of each amino acid and divide into 4 equal groups
    counter = collections.Counter(protein)
    char_list = sorted(counter, key=counter.get, reverse=True)
    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    duration_quartiles = lol(char_list, 4)

    notes = []
    duration = []

    for i, x1 in enumerate(protein):
        # get unicode value of amino acid character
        num1 = ord(x1)

        # retrieve note name and hertz value of note
        note_name = KEYS[key][num1 % len(KEYS[key])]
        note = NOTE_FREQ[note_name]

        # check if index is within conserved domain
        if i in all_reg:
            # get chord and combine with original note, add to notes list
            chord = get_chord(note_name, KEYS[key])
            chord.append(note)
            notes.append(chord)

        else:
            # if index is not witin conserved domain, just add single note
            notes.append([note])

        # determining duration of each note depending on quartiles
        if x1 in duration_quartiles[0]:
            # longest note
            dur = 8
        elif x1 in duration_quartiles[1]:
            # second longest
            dur = 4
        elif x1 in duration_quartiles[2]:
            dur = 2
        else:
            dur = 1

        duration.append(dur)

    return key, tempo, notes, duration


def color_domain(sequence, coding_regions):
    '''
    Adds colour to conserved domain region of protein
    Inputs: sequence- protein sequence as returned from NCBI
            coding_regions- list of lists containing conserved domains
    Outputs: colored_sequence- sequence with colour applied
    '''
    colored_sequence = ''
    current_index = 0
    # loop through each conserved domain pair of indices
    for region in coding_regions:
        # move to beginning of conserved domain
        colored_sequence += sequence[current_index:region[0]]
        # add opening span tag with color
        colored_sequence += '<span style="color:#2fbfaf;">'
        # move to end of conserved domain
        colored_sequence += sequence[region[0]:region[1]+1]
        colored_sequence += '</span>'
        # set the current index as one after the end of this domain
        current_index = region[1]+1

    # add the rest of the sequence that occurs after conserved domains
    colored_sequence += sequence[current_index:]

    return colored_sequence


def create_sheet(notes, durations):
    '''
    Generates sheet music from generated notes and note durations using
    abc notation
    Inputs: notes- list of lists containing hertz value for each note
            durations- list of note durations
    Returns: sheet_string- string that will be fed to Javascript library
        to create sheet music
    '''
    # start string with opening music bars
    sheet_string = "[|"
    total_duration = 0
    # loop through notes (hertz frequencies)
    for index, note in enumerate(notes):
        # each chord (even single notes) must begin and end with bracket
        sheet_string += '['
        for n in note:
            # add abc notation for frequency
            sheet_string += SHEET_NOTES[n]
            # add duration for note from durations list at index
            sheet_string += str(durations[index])
        sheet_string += ']'

        # keep track of total duration of song
        total_duration += durations[index]

        # mark new lines in the sheet music every 16 notes
        if index % 16 == 0 and index != 0:
            sheet_string += '\n'

    # indicate end of sheet music
    sheet_string += "|]"

    return sheet_string


def create_coding_regions(xml_text):
    '''
    Retrieves conserved domains within a protein from NCBI, strips uneccesary
    characters and appends ranges to list
    Inputs: xml_text- output from API call in xml format
    Returns: coding_regions- list of lists containing the start and stop index
        of each conserved domain within protein
    '''
    coding_regions = []
    # parse into xml to retrieve indices for locations following Region tags
    table = xml_text.GBSet.GBSeq.findAll('GBSeq_feature-table')
    for tag in table:
        key = tag.findAll('GBFeature')
        for k in key:
            content = k.GBFeature_key.contents
            if content[0] == 'Region':
                region = k.GBFeature_key.find_next('GBFeature_location').contents
                # find indices around indices in the content of the tag
                i = region[0].find('..')

                # strip < and > from thhe indices and set assign both indices
                # to start and stop variables
                if '<' in region[0] and '>' in region[0]:
                    start = int(region[0][:i].strip('<').strip('>'))
                    stop = int(region[0][i+2:].strip('<').strip('>'))
                elif '<' in region[0]:
                    start = int(region[0][:i].strip('<'))
                    stop = int(region[0][i+2:].strip('<'))
                elif '>' in region[0]:
                    start = int(region[0][:i].strip('>'))
                    stop = int(region[0][i+2:].strip('>'))
                else:
                    start = int(region[0][:i])
                    stop = int(region[0][i+2:])

                # append list of indices to list of all other indices
                coding_regions.append([start, stop])

    return coding_regions


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/song')
def make_song():
    acc_number = request.args.get('acc_number')
    try:
        # retrieve protein sequence and name using eutils API
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&rettype=gb&retmode=xml&id=' + acc_number
        r = requests.get(url)
        xml_text = BeautifulSoup(r.text, "xml")
        sequence = xml_text.GBSeq_sequence.contents[0]
        name = xml_text.GBSeq_definition.contents[0]

        # get coding regions
        coding_regions = create_coding_regions(xml_text)
        # run protein sequence through sonification algorithm
        key, tempo, notes, durations = map_protein(sequence, coding_regions)
        # create sheet music string
        sheet_string = create_sheet(notes, durations)
        # colour protein sequence text
        colored_sequence = color_domain(sequence, coding_regions)
        # cut off protein name if too long
        sheet_name = name if len(name) <= 60 else name[:60] + '...'

        return render_template('song.html', protein_seq=colored_sequence,
                               protein_name=name, notes=notes, durations=durations,
                               tempo=tempo, coding_regions=coding_regions,
                               sheet_string=sheet_string, key=key, sheet_name=sheet_name)

    except:
        error = "I'm sorry! <span style='color:#2fbfaf;'>{0}</span> is not a valid accession number. Click on <a href='/' style='color:#2fbfaf;'>BioMusic</a> to try again.".format(acc_number)
        return render_template('error.html', error=error)
