(function () {
    let workersSearch = new Vue({
        el: "#workersSearch",
        data: {
            workers: []
        },
        delimiters: ["[[","]]"],
        updated: function () {
            if (workersSearch.workers.length) {
                $(".worker-search-result-modal").show()
            } else {
                $(".worker-search-result-modal").hide()
            }
        },
        methods: {
            loadWorkers: function () {
                let params = {
                    'last_name': $("#id_last_name").val(),
                    'first_name': $("#id_first_name").val(),
                    'middle_name': $("#id_middle_name").val(),
                    'birth': $("#id_birth").val(),
                    'org': $("#id_org").val(),
                };

                $.get({
                    url: "/rest/workers/?per_page=10",
                    data: params,
                    traditional: true,
                    success: function (response) {
                        workersSearch.workers = response.results
                    }
                });
            },
            choiceWorker: function (worker) {
                $("#id_last_name").val(worker.last_name);
                $("#id_first_name").val(worker.first_name);
                $("#id_middle_name").val(worker.middle_name);
                $("#id_birth").val(worker.birth_rus);
                $("#id_gender").val(worker.gender);
                $("#id_post").val(worker.post);
                $("#id_shop").val(worker.shop);

                if (worker.org) {
                    let orgName = worker.org.legal_name ? worker.org.legal_name : worker.org.name
                    let opt = "<option value='" + worker.org.id + "' selected'>" + orgName + "</option>"
                    $("#id_org").html(opt)
                    $("#id_org").val(worker.org.id).trigger('change')
                }

                let lawItemsSection1 = [];
                worker.law_items_section_1.forEach(function (lawItem) {
                    lawItemsSection1.push(lawItem.id);

                    if (!!$("#id_law_items_section_1 option[value=" + lawItem.id + "]")) {
                        $("#id_law_items_section_1").append($("<option value=" + lawItem.id + ">" + lawItem.name + "</option>"))
                    }

                });

                let lawItemsSection2 = [];
                worker.law_items_section_2.forEach(function (lawItem) {
                    lawItemsSection2.push(lawItem.id);

                    if (!!$("#id_law_items_section_2 option[value=" + lawItem.id + "]")) {
                        $("#id_law_items_section_2").append($("<option value=" + lawItem.id + ">" + lawItem.name + "</option>"))
                    }
                });

                $("#id_law_items_section_1").val(lawItemsSection1).trigger("change.select2");
                $("#id_law_items_section_2").val(lawItemsSection2).trigger("change.select2");

                $(".worker-search-result-modal").hide()
            }
        }
    });

    $(".close-worker-search-result").click(function () {
        $(".worker-search-result-modal").hide()
    });

    $("#id_last_name, #id_first_name, #id_middle_name").on('keypress', function () {
        workersSearch.loadWorkers()
    })

}).call(this);
