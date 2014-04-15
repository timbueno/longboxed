$(function() {

  $( ".add-remove-pull" ).click(function() {
    var $star = $(this);
    var titleId = $(this).data("titleid")
    if ($(this).hasClass('on-pull-list')) {
      var iteration = 2;
    } else {
      var iteration = $(this).data('iteration')||1
    }
    switch (iteration) {
      case 1:
        $.post(
          '/ajax/add_to_pull_list',
          {'id': titleId}
        )
        .done(function() {
          // $star.toggleClass( "on-pull-list not-on-pull-list" );
          $star.removeClass( "not-on-pull-list" );
          $star.addClass( "on-pull-list" );
        });
        break;
      case 2:
        $.post(
          '/ajax/remove_from_pull_list',
          {'id': titleId}
        )
        .done(function() {
          // $star.toggleClass( "on-pull-list not-on-pull-list" );
          $star.removeClass( "on-pull-list" );
          $star.addClass( "not-on-pull-list" );
        });
        break;
    }
    iteration++;
    if (iteration>2) iteration=1;
    $(this).data('iteration', iteration);
  });


  function encodeData(data) {
    return Object.keys(data).map(function(key) {
      return [key, data[key]].map(encodeURIComponent).join("=");
    }).join("&");
  }

  $( ".tweet" ).click(function() {
    var baseUrl = "https://twitter.com/intent/tweet?";
    var parameters = {"url": $(this).data("url"), "via": "longboxed", "text": $(this).data("title")};
    window.open(baseUrl+encodeData(parameters), 'Longboxed | Tweet', 'height=450,width=500');
    return false;
  });

  $( ".facebook" ).click(function() {
    var baseUrl = "http://www.facebook.com/sharer.php?";
    // var parameters = {"p[url]": $(this).data("url")}
    var parameters = {
      "p[url]": $(this).data("url"),
      "p[title]": $(this).data("title"),
    };
    window.open(baseUrl+encodeData(parameters), 'Longboxed | Facebook Share', 'height=450,width=500');
  });

});