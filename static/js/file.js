$(document).ready(function(){
    $(".form-group-input").on("click", ".browse-file", function () {
        var file = $(this)
            .parent()
            .parent()
            .parent()
            .find(".file-input");
        file.trigger("click");
    });
    $(".form-group-input").on("change", ".file-input", function () {
        $(this)
            .parent()
            .find(".file-path")
            .val(
                $(this)
                    .val()
                    .replace(/C:\\fakepath\\/i, "")
            );
    });
    });