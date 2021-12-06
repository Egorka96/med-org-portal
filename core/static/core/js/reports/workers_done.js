(function () {
    $(".report-table").removeClass("table-striped table-hover")

    let ordersParams = $.map($('.order-documents-btn'), function (btn) {
        return $(btn).data('document-orders-params')
    }).reverse()

    let loadOrdersDocuments = function () {
        if (ordersParams.length !== 0) {
            let ordersParam = ordersParams.pop()
            $.get({
                url: '/rest/documents/choices/',
                data: {
                    search_params: ordersParam
                },
                success: function (response) {
                    let ordersDocumentBtn = $($.find(`[data-document-orders-params="${ordersParam}"]`))
                    let clientFIO = ordersDocumentBtn.data('client-fio')
                    ordersDocumentBtn.parents("td").children(".badge-loading").hide()

                    // todo: проверять, если пользователю доступен всего один вид документа, до кнопка сразу должна быть ссылкой
                    if (response.length) {
                        let content = '<ul class="orders-documents-list">'
                        for (let i = 0; i < response.length; i++) {
                            let document = response[i]
                            let fileName = encodeURIComponent(`${clientFIO} ${document.doc_type.name}`)
                            content += `
                                <li class="orders-documents-item">
                                    <a href="/rest/documents/print/?link=${encodeURIComponent(document.doc_link)}&name=${fileName}" target="_blank">
                                        ${document.doc_type.name}
                                    </a>
                                </li>
                            `
                        }
                        content += "</ul>"

                        ordersDocumentBtn.show()
                        ordersDocumentBtn.popover({
                            container: 'body',
                            trigger: 'focus',
                            content: content,
                            html: true,
                            title: "Документы"
                        })
                    }
                    loadOrdersDocuments()
                }
            }).fail(function (response) {
                console.error('Что-то пошло не так: ', response)
            })
        }
    }
    loadOrdersDocuments()
}).call(this)