// $(document).ready(function() {
    // $('.testbutton').click(function(){
    //     var new_favorite = $("input#newfavorite").val();
    //     $.post(
    //         '/ajax/add_favorite',
    //         {'new_favorite': new_favorite},
    //         function(data){
    //             if (data.success==true){
    //                 $('div.favorites').html(data.html);
    //                 remove_favorite();
    //                 alertify.success('Successfully added \''+new_favorite+'\' to your Pull List!');
    //                     $("input#newfavorite").val('');
    //             }
    //             else {
    //                 alertify.log('\''+new_favorite+'\' is already on your Pull List');
    //                 $("input#newfavorite").val('');
    //             }
    //         }
    //     );
    //     return false;
    // });
$('#submit_pull').click(function(){
    var token = $("input#csrf_token").val();
    console.log(token);
    var title = $("input#title").val();
    $.post(
        '/ajax/add_to_pull_list',
        {   
            'csrf_token': token,
            'title': title
        }
        // function(data){
        //     console.log(data);
        //     if (data.success==true){
        //         $('div.favorites').html(data.html);
        //         remove_favorite();
        //         alertify.success('Successfully added \''+new_favorite+'\' to your Pull List!');
        //             $("input#newfavorite").val('');
        //     }
        //     else {
        //         alertify.log('\''+new_favorite+'\' is already on your Pull List');
        //         $("input#newfavorite").val('');
        //     }
        // }
    )
    .done(function(response) {
        console.log(response);
        if (response.success==true){
            $('div.favorites').html(response.html);
            remove_favorite();
            alertify.success('Successfully added \''+title+'\' to your Pull List!');
                $("input#newfavorite").val('');
        }
        else {
            alertify.log('\''+title+'\' is already on your Pull List');
            $("input#newfavorite").val('');
        }
    })
    .fail(function(response){
        console.log('FAIL!');
    });
    return false;
});
// })