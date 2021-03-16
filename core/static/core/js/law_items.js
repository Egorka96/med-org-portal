(function () {
    $(function () {
        let initialLawItemSelect2 = function (law, section) {
            let fieldId = `#id_law_items_${law}`
            if (section) {
                fieldId += `_section_${section}`
            }

            $(fieldId).select2({
                language: "ru",
                theme: "bootstrap",
                ajax: {
                    url: "/rest/law_items/",
                    dataType: 'json',
                    cache: true,
                    traditional: true,
                    data: function (params) {
                        params['law_name'] = `${law}н`
                        if (section) {
                            params['section'] = section
                        }
                        return params
                    },
                    processResults: function (data, params) {
                        params.page = params.page || 1;
                        return {
                            results: data.results,
                            pagination: {
                                more: data['next']
                            }
                        };
                    }
                },
                escapeMarkup: function (markup) {
                    return markup
                },
                templateResult: function (data, container) {
                    return data.name || data.text
                },
                templateSelection: function (data, container) {
                    return data.name || data.text
                }
            });
        };

        initialLawItemSelect2('302', 1);
        initialLawItemSelect2('302', 2);
        initialLawItemSelect2('29');
    });
}).call(this);

