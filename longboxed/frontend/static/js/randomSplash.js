/**
 * Returns a random integer between min (inclusive) and max (inclusive)
  * Using Math.round() will give you a non-uniform distribution!
   */
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var splashImages = [
    "/static/img/ultron-bw.jpg",
    "/static/img/header-bg.jpg",
    "/static/img/slide-01.jpg",
    "/static/img/slide-02.jpg"
];
// Get random splash image
splashImage = splashImages[getRandomInt(0, (splashImages.length-1))];
// Set background image
$('.headerwrap').css('background-image', 'url(' + splashImage + ')');

