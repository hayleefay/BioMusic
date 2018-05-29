from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


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

        notes = []
        for acid in sequence:
            notes.append(196.00)
            notes.append(311.13)

        return render_template('song.html', protein_seq=sequence, protein_name=name, notes=notes, coding_regions=coding_regions)

    error = 'sorry'
    return render_template('error.html', error=error)
