$(function () {
    // Show a confirm dialog box when trying to delete a file
    $("#del-btn").click(function(){
        bootbox.confirm("Are you sure you want to delete this file?", function(result) {
            if (result == true){
                $("#del-frm").submit();
            }
        });
    });

    // Show a modify dialog box when trying to edit metadata.
    $("#modify-btn").click(function() {
        var form_name = "modify-frm"
        var hidden_name_id = "#hidden-" + form_name
        // Read form template from html
        var modal_form = $(hidden_name_id).html();
        var modal_title = $(hidden_name_id).attr('modalTitle');
        var modal_focus = $(hidden_name_id).attr('modalFocus');
        // A bit of a hack to avoid implementing this from scratch
        // using .dialog().
        var box = bootbox.confirm({
            title: modal_title,
            message: modal_form,
            centerVertical: true,
            onShown: function(e) {
                if (modal_focus) {
                    $(this).find("#" + modal_focus).trigger('focus');
                }
                // Support jquery-ui autocomplete
                contenttype_autocomplete(this)
            },
            callback: function(result) {
                // Please note that this is not called when hitting
                // the Enter key on the input box.
                if (result == true) {
                    $(this).find("#" + form_name).submit();
                }
            }
        });
    });

    // Bind on click event to all line number anchor tags
    $('td.linenos a').on('click', function(e) {
        remove_highlights();
        var $this = $(this);
        var line_number = $this.text().trim();
        highlight_line(line_number);
    });

    // Check the value of the hash in the URL on first load
    var line_number = get_hash_line_number();
    if (line_number != null) {
        highlight_line(line_number);
    }

    // Bind hashchange event
    $(window).bind('hashchange', function(e){
        remove_highlights();
        var line_number = get_hash_line_number();
        if (line_number != null) {
            highlight_line(line_number);
        }
    });
});

// Highlight one line
function highlight_line(line_number) {
    var line = $('#L-' + line_number);
    $(line).addClass("line-highlight");
}

// Remove highlighting from all lines
function remove_highlights() {
    $('td.code p').removeClass("line-highlight");
}

// Get the number line from the hash if there is one, otherwise return null
function get_hash_line_number() {
    var type = window.location.hash;
        if (type.indexOf("-") > -1) {
            return type.split("-")[1];
        }
    return null;
}
