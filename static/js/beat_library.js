var last_caller = null

function play(url, caller) {
    let old = document.getElementById("audio").getAttribute("src");
    if (old == url) {
        stop(caller)
        return
    };
    document.getElementById("audio").setAttribute("src", url);
    let audio = document.getElementById("audio");
    audio.play();
    if (last_caller != null) {
      document.getElementById(last_caller).innerHTML = '<i class="fa-solid fa-play"></i>Play'
    };
    document.getElementById(caller).innerHTML = '<i class="fa-solid fa-stop"></i>Stop';
    last_caller = caller;
}

function stop(caller) {
    let audio = document.getElementById("audio");
    audio.pause();
    audio.currentTime = 0;
    document.getElementById("audio").setAttribute("src", "");
    document.getElementById(caller).innerHTML = '<i class="fa-solid fa-play"></i>Play';
}

// Event listening:

const boxes = document.querySelectorAll('.play-button');
boxes.forEach(play_button => {
  play_button.addEventListener('click', function handleClick(event) {
    const value = event.target.value; // event's `target` property is useful
    play(value, this.id);
  });
});

var audio = document.getElementById('audio')
audio.addEventListener('timeupdate', function updateSeek(event) {
    document.getElementById("seekbar").setAttribute("value", this.currentTime / this.duration);
})