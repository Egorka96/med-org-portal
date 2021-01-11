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

                        if (Object.keys(response.documents).length) {
                            let content = ''
                            $.each(response.documents, function(date, documents) {
                                content += `<h5>${date}</h5><ul>`
                                for (let i = 0; i < documents.length; i++) {
                                    let document = documents[i]
                                    content += `<li><a href="">${document.document_type.name}</a> </li>`
                                }
                                content += "</ul><hr>"
                            });

                            workerDocumentBtn.show()
                            workerDocumentBtn.popover({
                                container: 'body',
                                trigger: 'focus',
                                content: content,
                                html: true
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