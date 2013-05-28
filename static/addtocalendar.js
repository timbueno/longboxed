var add2cal = function(){
    $('.add2cal').each(
        function(){
            var $pElem = $(this);
            var $id = $pElem.attr('data-id');
            $pElem.click(
                function(){
                    // console.log($id);
                    $.get(
                        '/add_issue_to_cal',
                        {'id': $id},
                        function(data){
                            // console.log(data);
                            if (data.response==200){
                                alertify.success('Successfully added '+data.title+' to your calendar!');
                            }
                            else if (data.response==201){
                                alertify.log('Comic has already been added!');
                            }
                            else {
                                alertify.error('Something went wrong');
                            }
                        }
                    )
                }
            );
        }
    );
}

