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
                $(".alert-box").append(
                    "<div class=\"alert alert-success alert-dismissable\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>"+response.data.title+"</strong> has been added to your Pull List!</div>"
                );
                remove_from_pull_list();
            }
            else if (response.status=='fail'){
                $("input#title").val('');
                $(".alert-box").append(
                    "<div class=\"alert alert-warning alert-dismissable\"><button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button>"+response.message+"</div>"
                );
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

// var setup_typeahead = function(){
//     // $('.example-countries .typeahead').typeahead({                                
//     //   name: 'countries',                                                          
//     //   prefetch: '../data/countries.json',                                         
//     //   limit: 10                                                                   
//     // });
//     $('.typeahead').typeahead({
//         name: 'titles',
//         prefetch: '/ajax/typeahead',
//         limit: 10
//     }).each(function() {
//        if ($(this).hasClass('input-lg'))
//             $(this).prev('.tt-hint').addClass('hint-lg');
       
//        if ($(this).hasClass('input-sm'))
//             $(this).prev('.tt-hint').addClass('hint-sm');
//     });
// };

// Setup the page
add_to_pull_list();
remove_from_pull_list();
// setup_typeahead();





