from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/song', methods=['POST'])
def make_song():
    if request.method == 'POST':
        acc_number = request.form['acc_number']
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&rettype=fasta&id=' + acc_number
        r = requests.get(url)
        lines = r.text.split('\n')
        protein_name = lines[0]

        protein_seq = ''
        for index, line in enumerate(lines):
            if index == 0:
                continue
            protein_seq += line

        notes = []
        for acid in protein_seq:
            notes.append(196.00)
            notes.append(311.13)

        return render_template('song.html', protein_seq=protein_seq, protein_name=protein_name, notes=notes)

    error = 'sorry'
    return render_template('error.html', error=error)
