(function () {
    $('.generate-password').click(function() {
        return $.get({
            url: "/rest/generate_password/",
            success: function(data) {
                return $('#id_new_password').val(data.password);
            }
        });
    });

    $(".btn-save").click(function () {
        if (canSendUserCredentials && $("#id_new_password").val() && $("#id_email").val()) {
            $("#needSendPasswordEmailModal").modal('show')
        } else {
            $('form').submit()
        }
    })

}).call(this)