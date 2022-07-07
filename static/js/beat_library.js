function play(url) {
    document.getElementById("audio").setAttribute("src", url);
    let audio = document.getElementById("audio");
    audio.play();
}

const play_buttons = document.querySelectorAll('.play-button');
play_buttons.forEach(play_button => {
  play_button.addEventListener('click', function handleClick(event) {
    const value = event.target.value; // event's `target` property is useful
    play(value);
  });
});


// Draggable scroll bar functionality:

var audio = document.querySelectorAll('audio');
var playBtn = document.querySelectorAll('.play');
var seekBar = document.querySelectorAll('.seek-bar');
var fillBar = document.querySelectorAll('.fill');
var seek = document.querySelectorAll('.seek');
var seeking = false;
var playing = undefined;

function updateProgress(i) {
  var duration = audio[i].duration;
  var multiplier = 100 / duration;
  var currentTime = audio[i].currentTime;
  seek[i].value = currentTime * multiplier;
}

function resetAudio(i) {
  audio[i].currentTime = 0;
  updateProgress(i, 0);
}

function handleSeek(e, i) {
  seeking = true;
  var seekPosition = e.target.value / 100;
  var playFrom = audio[i].duration * seekPosition;
  handleAudioPlayback(i, playFrom);
  updateProgress(i);
}

function handleButtonClick(i, time) {
  if (playing === undefined) {
    playing = i;
  }
  handleAudioPlayback(i, time);
}

function handleAudioPlayback(i, time) {
  var seekPosition = seek[i].value;
  if (playing !== i && !seeking) {
    audio[playing].pause();
    playing = i;
  }
  var a = audio[i];
  if (seeking) {
    a.currentTime = time;
    seeking = false;
  } else if (a.paused) {
    a.play();
  } else {
    a.pause();
  }
}

audio.forEach((node, i) => {
  node.addEventListener('timeupdate', function(e) {
    updateProgress(i);
  });
  node.addEventListener('ended', function(e) {
    resetAudio(i);
  });
  playBtn[i].addEventListener('click', function(e) {
    handleButtonClick(i, 0);
  });
  seek[i].addEventListener('change', function(e) {
    handleSeek(e, i);
  });
});