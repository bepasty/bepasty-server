$(function () {
    // Show a confirm dialog box when trying to delete a file
    $("#del-btn").click(function(){
        bootbox.confirm("Are you sure you want to delete this file?", function(result) {
            if (result == true){
                $("#del-frm").submit();
            }
        });
    });
});