(function () {
    let prepareOrgs;
    let ORG_REST_URL = "/rest/orgs/";

    $(function () {
        prepareOrgs();
    });

    prepareOrgs = function () {
        let initialSelect2 = function () {
            $('#id_orgs').not(':hidden').select2({
                language: "ru",
                theme: "bootstrap",
                ajax: {
                    url: ORG_REST_URL,
                    dataType: 'json',
                    cache: true,
                    traditional: true,
                    data: function (params) {
                        return params
                    },
                    processResults: function (data, params) {
                        params.page = params.page || 1;
                        return {
                            results: data.results,
                            pagination: {
                                more: data['more']
                            }
                        };
                    }
                },
                escapeMarkup: function (markup) {
                    return markup
                }
            })
        };
        initialSelect2();
    }

}).call(this);