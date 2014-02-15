var remove_from_pull_list = function(){
    $('#user-pull-list li').each(function(){
        var $liElem = $(this);
        var $iElem = $(this).children('i');
        var id = $liElem.attr('data-id');
        $iElem.click(function(){
            $.post(
                '/ajax/remove_from_pull_list',
                {'id': id}
            )
            .done(function(response) {
                if (response.status=='success'){
                    $liElem.remove();
                    // alertify.success(response.message);
                }
            });
        });
    });
};

var add_to_pull_list = function(){
    $('#submit_pull').click(function(){
        var token = $("input#csrf_token").val();
        var title = $("input#title").val();
        $.post(
            '/ajax/add_to_pull_list',
            {   
                'csrf_token': token,
                'title': title
            }
        )
        .done(function(response){
            if (response.status=='success'){
                $('#user-pull-list').append(
                    "<li class=\"list-group-item\" data-id="+response.data.title_id+" data-name=\""+response.data.title+"\" >"+response.data.title+"<i class=\"fa fa-times pull-right remove-button\"></i></li>"
                ); 
                $("input#title").val('');
                $('.typeahead').typeahead('val', '');
                $(".alert-box").append(
                    "<div class=\"alert alert-success alert-dismissable title-"+response.data.title_id+"\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>"+response.data.title+"</strong> has been added to your Pull List!</div>"
                );
                remove_from_pull_list();
                // Fade out alert after 5 Seconds
                window.setTimeout(function() {
                    $(".title-"+response.data.title_id).fadeTo(500, 0).slideUp(500, function(){
                        $(this).remove(); 
                    });
                }, 5000);
            }
            else if (response.status=='fail'){
                $("input#title").val('');
                $('.typeahead').typeahead('val', '');
                $(".alert-box").append(
                    "<div class=\"alert alert-warning alert-dismissable title-"+response.data.title_id+"\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button>"+response.message+"</div>"
                );
                // Fade out alert afer 5 Seconds
                window.setTimeout(function() {
                    $(".title-"+response.data.title_id).fadeTo(500, 0).slideUp(500, function(){
                        $(this).remove(); 
                    });
                }, 5000);
            }
            else {
                $("input#title").val('');
                $(".alert-box").append(
                    "<div class=\"alert alert-danger alert-dismissable\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">Something went wrong!</div>"
                );
            }
        })
        .fail(function(response){
        });
        return false;
    });
};

// instantiate the bloodhound suggestion engine
var titles = new Bloodhound({
    datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.title); },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: {
        url: '/ajax/typeahead',
        ttl: 0
    }
});
 
// initialize the bloodhound suggestion engine
titles.initialize();

// Compile the Template
var suggestion_template = Handlebars.compile([
    '<p class="suggest-publisher">{{publisher}}</p>',
    '<p class="suggest-title">{{title}}</p>',
    '<p class="suggest-description">{{users}} Subscribers</p>'
].join(''));
 
// instantiate the typeahead UI
$('.typeahead').typeahead(null, 
{
    name: 'titles',
    displayKey: 'title',
    source: titles.ttAdapter(),
    templates: {
        suggestion: suggestion_template
    }
});

// Setup the page
add_to_pull_list();
remove_from_pull_list();
// setup_typeahead();





