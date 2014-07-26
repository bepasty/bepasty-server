$(function () {
    // Show a confirm dialog box when trying to delete a file
    $("#del-btn").click(function(){
        bootbox.confirm("Are you sure you want to delete this file?", function(result) {
            if (result == true){
                $("#del-frm").submit();
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
