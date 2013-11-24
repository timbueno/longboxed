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
                $('div.favorites').html(response.data.html);
                // remove_favorite();
                alertify.success(response.message);
                $("input#title").val('');
                remove_from_pull_list();
            }
            else if (response.status=='fail'){
                alertify.log(response.message);
                $("input#title").val('');
            }
            else {
                alertify.error(response.message);
            }
        })
        .fail(function(response){
            alertify.error('Something went wrong...');
        });
        return false;
    });
};

var remove_from_pull_list = function(){
    $('#titles-on-pull-list li').each(function(){
        var $liElem = $(this);
        var $iElem = $(this).children('i');
        var id = $liElem.attr('data-id');
        // var $name = $pElem.attr('data-name');
        $liElem.click(function(){
            $.post(
                '/ajax/remove_from_pull_list',
                {'id': id}
            )
            .done(function(response) {
                if (response.status=='success'){
                    $liElem.remove();
                    alertify.success(response.message);
                }
            });
        });
    });
};

var setup_typeahead = function(){
    // $('.example-countries .typeahead').typeahead({                                
    //   name: 'countries',                                                          
    //   prefetch: '../data/countries.json',                                         
    //   limit: 10                                                                   
    // });
    $('.typeahead').typeahead({
        name: 'titles',
        prefetch: '/ajax/typeahead',
        limit: 10
    }).each(function() {
       if ($(this).hasClass('input-lg'))
            $(this).prev('.tt-hint').addClass('hint-lg');
       
       if ($(this).hasClass('input-sm'))
            $(this).prev('.tt-hint').addClass('hint-sm');
    });
};

// Setup the page
add_to_pull_list();
remove_from_pull_list();
setup_typeahead();





