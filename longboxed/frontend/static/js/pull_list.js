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
            else if (reponse.status=='error'){
                alertify.error(response.message);
            }
        })
        .fail(function(response){
            alertify.error('Something went wrong...');
        });
        return false;
    });
}

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


// Setup the page
add_to_pull_list();
remove_from_pull_list();






