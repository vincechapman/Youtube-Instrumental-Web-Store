function fadeInPage() {
    if (!window.AnimationEvent) { return; }
    var fader = document.getElementById('paypal-fader');
    fader.classList.add('fade-out');
    fader.setAttribute('class', 'fade-out');
}

document.addEventListener('DOMContentLoaded', function() {
    if (!window.AnimationEvent) { return; }
    var purchaseButton = document.getElementsByClassName('purchase-button');
    
    for (var idx=0; idx<purchaseButton.length; idx+=1) {
        purchaseButton[idx].addEventListener('click', function(event) {
            var fader = document.getElementById('paypal-fader'),
                anchor = event.currentTarget;
            
            var listener = function() {
                fader.removeEventListener('animationend', listener);
            };
            fader.addEventListener('animationend', listener);
            
            event.preventDefault();
            fader.classList.add('fade-in');
            fader.setAttribute('class', 'fade-in');
            fader.style.display = 'initial';
        });
    }
});

window.addEventListener('pageshow', function (event) {
    if (!event.persisted) {
      return;
    }
    var fader = document.getElementById('paypal-fader');
    fader.classList.remove('fade-in');
    fader.removeAttribute('class', 'fade-in');
  });
