(function () {
    $(function () {
        let initialLawItemSelect2 = function (section) {
            $("#id_law_items_section_" + section).select2({
                language: "ru",
                theme: "bootstrap",
                ajax: {
                    url: "/rest/law_items/?section=" + section,
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
            });
        };

        initialLawItemSelect2(1);
        initialLawItemSelect2(2);
    });


}).call(this);

