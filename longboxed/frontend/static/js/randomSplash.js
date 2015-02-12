/**
 * Returns a random integer between min (inclusive) and max (inclusive)
  * Using Math.round() will give you a non-uniform distribution!
   */
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

var splashImages = [
    "/static/img/splash/ultron-bw.jpg",
    "/static/img/splash/hulk-bw.jpg",
    "/static/img/splash/marvel-assorted-bw.jpg",
    "/static/img/splash/sandman-bw.jpg",
    "/static/img/splash/rorschach-bw.jpg",
    "/static/img/splash/dc-assorted-bw.jpg",
    "/static/img/splash/batman-bw.jpg"
];
// Get random splash image
var splashImage = splashImages[getRandomInt(0, (splashImages.length-1))];
// Set background image
$('.headerwrap').css('background-image', 'url(' + splashImage + ')');

