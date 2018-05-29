from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from itertools import chain

app = Flask(__name__)

NOTE_FREQ = {'C#_1': 277.18, 'D#_1': 207.65, 'F#_1': 369.99, 'G#_1': 415.30,
             'A#_1': 466.16, 'C#_2': 554.37, 'D#_2': 622.25, 'F#_2': 739.99,
             'G#_2': 830.61, 'A#_2': 932.33, 'G_1': 196.00, 'A_1': 220.00,
             'B_1': 246.94, 'C_1': 261.63, 'D_1': 293.66, 'E_1': 329.63,
             'F_1': 349.23, 'G_2': 392.00, 'A_2': 440.00, 'B_2': 493.88,
             'C_2': 523.25, 'D_2': 587.33, 'E_2': 659.25, 'F_2': 698.46,
             'G_3': 783.99, 'A_3': 880.00, 'B_3': 987.77, 'C_3': 1046.50}

SHEET_NOTES = {207.65: 'D', 369.99: 'F', 415.30: 'G', 466.16: 'A',
               554.37: 'C', 622.25: 'D', 739.99: 'f', 830.61: 'g',
               932.33: 'a', 196.00: 'G', 220.00: 'A', 246.94: 'B',
               261.63: 'C', 293.66: 'D', 329.63: 'E', 349.23: 'F',
               392.00: 'g', 440.00: 'a', 493.88: 'b', 523.25: 'c',
               587.33: 'd', 659.25: 'e', 698.46: 'f', 783.99: "g",
               880.00: "a", 987.77: "b", 1046.50: "c", 277.18: 'C'}

NOTE_LIST = list(NOTE_FREQ.keys())

C_MAJOR = ['G_1', 'A_1', 'B_1', 'C_1', 'D_1', 'E_1', 'F_1', 'G_2', 'A_2', 'B_2', 'C_2', 'D_2', 'E_2', 'F_2', 'G_3', 'A_3', 'B_3', 'C_3']
G_MAJOR = ['G_1', 'A_1', 'B_1', 'C_1', 'D_1', 'E_1', 'F#_1', 'G_2', 'A_2', 'B_2', 'C_2', 'D_2', 'E_2', 'F#_2', 'G_3', 'A_3', 'B_3', 'C_3']
D_MAJOR = ['G_1', 'A_1', 'B_1', 'C#_1', 'D_1', 'E_1', 'F#_1', 'G_2', 'A_2', 'B_2', 'C#_2', 'D_2', 'E_2', 'F#_2', 'G_3', 'A_3', 'B_3']

KEYS = {'Cmaj': C_MAJOR, 'Gmaj': G_MAJOR, 'Dmaj': D_MAJOR}
KEY_LIST = ['Cmaj', 'Gmaj', 'Dmaj']
TEMPOS = [70, 120, 250]
DURATIONS = [1, 2, 4, 8]


def get_chord(note, key_list):
    i = key_list.index(note)

    if i % 2 == 0:
        i1 = 2
        i2 = 4
    else:
        i1 = 3
        i2 = 5
    try:
        note1 = NOTE_FREQ[key_list[i + i1]]
        note2 = NOTE_FREQ[key_list[i + i2]]
    except:
        note1 = NOTE_FREQ[key_list[i - i1]]
        note2 = NOTE_FREQ[key_list[i - i2]]

    return [note1, note2]


def map_protein(protein, regions):
    all_reg = []
    for reg in regions:
        all_reg.append(list(range(reg[0], reg[1])))

    all_reg = list(chain(*all_reg))

    start = protein[:10]

    t = [ord(x) for x in start[:5]]
    k = [ord(x) for x in start[5:]]

    tempo = TEMPOS[sum(t) % 3]
    key = KEY_LIST[sum(k) % 3]

    notes = []
    duration = []

    for i, (x1, x2) in enumerate(zip(protein[0::2], protein[1::2])):
        num1 = ord(x1)
        num2 = ord(x2)

        note_name = KEYS[key][num1 % len(KEYS[key])]
        note = NOTE_FREQ[note_name]

        if i in all_reg:
            # get note
            chord = get_chord(note_name, KEYS[key])

            chord.append(note)

            notes.append(chord)

        else:
            notes.append([note])

        dur = num2 % 4

        duration.append(DURATIONS[dur])

    return key, tempo, notes, duration


def color_domain(sequence, coding_regions):
    colored_sequence = ''
    current_index = 0
    for region in coding_regions:
        colored_sequence += sequence[current_index:region[0]]
        colored_sequence += '<span style="color:#2fbfaf;">'
        colored_sequence += sequence[region[0]:region[1]+1]
        colored_sequence += '</span>'
        current_index = region[1]+1

    colored_sequence += sequence[current_index:]

    return colored_sequence


def create_sheet(notes, durations):
    sheet_string = ""
    total_duration = 0
    for index, note in enumerate(notes):
        sheet_string += SHEET_NOTES[note[0]]

        sheet_string += str(durations[index])

        total_duration += durations[index]

        if total_duration % 4 == 0 and total_duration != 0:
            sheet_string += '|'

        if total_duration % 16 == 0:
            sheet_string += '\n'

    return sheet_string


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/song', methods=['POST'])
def make_song():
    if request.method == 'POST':
        acc_number = request.form['acc_number']
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&rettype=gb&retmode=xml&id=' + acc_number
        r = requests.get(url)
        xml_text = BeautifulSoup(r.text, "xml")
        sequence = xml_text.GBSeq_sequence.contents[0]
        name = xml_text.GBSeq_definition.contents[0]

        coding_regions = []
        table = xml_text.GBSet.GBSeq.findAll('GBSeq_feature-table')
        for tag in table:
            key = tag.findAll('GBFeature')
            for k in key:
                content = k.GBFeature_key.contents
                if content[0] == 'Region':
                    region = k.GBFeature_key.find_next('GBFeature_location').contents
                    i = region[0].find('..')
                    start = int(region[0][:i])
                    stop = int(region[0][i+2:])
                    coding_regions.append([start, stop])

        key, tempo, notes, durations = map_protein(sequence, coding_regions)

        sheet_string = create_sheet(notes, durations)

        colored_sequence = color_domain(sequence, coding_regions)

        return render_template('song.html', protein_seq=colored_sequence, protein_name=name, notes=notes, durations=durations, tempo=tempo, coding_regions=coding_regions, sheet_string=sheet_string, key=key)

    error = 'sorry'
    return render_template('error.html', error=error)
