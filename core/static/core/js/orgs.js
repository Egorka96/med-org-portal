(function () {
    let prepareOrgs;
    let ORG_REST_URL = "/rest/orgs/";

    $(function () {
        prepareOrgs();
    });

    prepareOrgs = function () {
        let initialSelect2 = function () {
            $('#id_org, #id_orgs').select2({
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
                },
                templateResult: function (data, container) {
                    return data.legal_name || data.name || data.text
                },
                templateSelection: function (data, container) {
                    return data.legal_name || data.name || data.text
                }
            })
        };
        initialSelect2();
    }

}).call(this);