class Sound {

  constructor(context) {
    this.context = context;
  }

  setup() {
    this.oscillator = this.context.createOscillator();
    this.gainNode = this.context.createGain();

    this.oscillator.connect(this.gainNode);
    this.gainNode.connect(this.context.destination);
    this.oscillator.type = 'sine';
  }

  play(value, start_time) {
    this.setup();

    this.oscillator.frequency.value = value;
    this.gainNode.gain.setValueAtTime(0, start_time);
    this.gainNode.gain.linearRampToValueAtTime(1, start_time + 0.01);

    this.oscillator.start(start_time);
    this.stop(start_time);
  }

  stop() {
    this.gainNode.gain.exponentialRampToValueAtTime(0.001, start_time + 1);
    this.oscillator.stop(this.context.currentTime + 1);
  }

}

function playSound(note) {
  let sound = new Sound(context);
  let value = note;
  sound.play(value);
  sound.stop();
}

function startSong() {
    var notes = $('#notes').data("notes");
    console.log(notes)

    let context = new (window.AudioContext || window.webkitAudioContext)();

    start_time = this.context.currentTime
    for (i = 0; i < notes.length; i++) {
      playSound(notes[i], start_time)
      start_time += 0.5
      console.log(start_time)
    }
  }
