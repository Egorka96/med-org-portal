(function () {
    $(function () {
        // по-умолчанию, будем прятать параметры фильтрации
        $("#searchFrom").hide()
        $(".btn-show-search-form").click(function () {
            $("#searchFrom").show()
            $(".btn-show-search-form").hide()
        })
        $(".btn-hide-search-form").click(function () {
            $("#searchFrom").hide()
            $(".btn-show-search-form").show()
        })

        // вычислим максимальную высоту карточки с сотрудников и присвоем эту высоту всем карточкам
        let workerCardHeights = $.map($('.card-worker-info'), function (item) {
            return $(item).height()
        })
        $('.card-worker-info').height(Math.max.apply(Math, workerCardHeights))

        $(".worker-documents-btn").hide()
        let workerIds = $.map($('.worker-documents-btn'), function (btn) {
            return $(btn).data('worker-id')
        }).reverse()

        let loadWorkersDocuments = function () {
            if (workerIds.length !== 0) {
                let workerId = workerIds.pop()
                $.get({
                    url: '/rest/worker_documents/',
                    data: {
                        worker: workerId
                    },
                    success: function (response) {
                        let workerDocumentBtn = $($.find(`[data-worker-id="${workerId}"]`))
                        let workerFIO = workerDocumentBtn.data('worker-fio')
                        workerDocumentBtn.parents("div").children(".badge-loading").hide()

                        if (response.documents.length) {
                            let content = '<ul class="worker-documents-list">'
                            for (let i = 0; i < response.documents.length; i++) {
                                let document = response.documents[i]
                                let fileName = encodeURIComponent(`${workerFIO} ${document.document_type.name}`)
                                content += `
                                    <li class="worker-documents-item">
                                        <a href="/rest/documents/print/?link=${encodeURIComponent(document.document_link)}&name=${fileName}" target="_blank">
                                            ${document.document_type.name}
                                        </a> 
                                        <span class="help-block">${document.date}</span>
                                    </li>
                                    `
                            }
                            content += "</ul>"

                            workerDocumentBtn.show()
                            workerDocumentBtn.popover({
                                container: 'body',
                                trigger: 'focus',
                                content: content,
                                html: true,
                                title: "Документы сотрудника"
                            })
                        } else {

                        }
                        loadWorkersDocuments()
                    }
                }).fail(function (response) {
                    console.error('Что-то пошло не так: ', response)
                })
            }
        }

        return loadWorkersDocuments()
    });
}).call(this);