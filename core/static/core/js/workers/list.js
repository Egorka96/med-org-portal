(function () {
    $(function () {
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
                        worker_mis_id: workerId
                    },
                    success: function (response) {
                        let workerDocumentBtn = $($.find(`[data-worker-id="${workerId}"]`))
                        workerDocumentBtn.parents("div").children(".badge-loading").hide()

                        if (response.documents.length) {
                            let content = '<ul class="worker-documents-list">'
                            for (let i = 0; i < response.documents.length; i++) {
                                let document = response.documents[i]
                                content += `<li class="worker-documents-item">
                                                <a href="">${document.document_type.name}</a> 
                                                <span class="help-block">${document.date}</span>
                                            </li>`
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