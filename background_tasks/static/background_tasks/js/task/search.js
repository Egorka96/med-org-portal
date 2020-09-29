$(function () {
    function prepareCancel() {
        $('button[name=cancel]').click(function () {
            let taskId = $(this).val()

            $.ajax({
                url: "/background_tasks/rest/task/" + taskId + "/cancel/",
                method: 'put',
                success: function () {
                    $.toast({
                        heading: '',
                        text: 'Задача отменена',
                        icon: 'info',
                        showHideTransition: 'fade',
                        stack: 1,
                        position: 'top-right'
                    })
                }
            }).fail(function () {
                $.toast({
                    heading: '',
                    text: 'Ошибка отмены задачи',
                    icon: 'error',
                    showHideTransition: 'fade',
                    stack: 1,
                    position: 'top-right'
                })
            })
        })
    }

     function prepareRestart() {
        $('button[name=restart]').click(function () {
            taskId = $(this).val()

            $.ajax({
                url: "/background_tasks/rest/task/" + taskId + "/restart/",
                method: 'put',
                success: function () {
                    $.toast({
                        heading: '',
                        text: 'Задача перезапущена',
                        icon: 'info',
                        showHideTransition: 'fade',
                        stack: 1,
                        position: 'top-right'
                    })
                }
            }).fail(function () {
                $.toast({
                    heading: '',
                    text: 'Ошибка перезапуска задачи',
                    icon: 'error',
                    showHideTransition: 'fade',
                    stack: 1,
                    position: 'top-right'
                })
            })
        })
    }

    function renderTask(task) {
        let tr = $("#task_" + task.id);

        // статус
        tr.removeClass('success').removeClass('danger');

        if (task.is_success) {
            tr.addClass('success');
        }
        if (task.is_fail) {
            tr.addClass('danger')
        }

        // прогресс
        let progress = tr.find('.progress')
        if (!task.start_dt || task.finish_dt) {
            progress.hide()
            tr.find('.task-status').text(task.status).show()
        } else {
            tr.find('.task-status').text(task.status).hide()
            progress.show()
            progress.find('.progress-bar')
                .attr('aria-valuenow', task.percent)
                .css('width', "#{ task.percent }%")
                .text("#{ task.percent }%")
        }

        tr.find('.start-dt').text(task.start_dt_rus)
        tr.find('.finish-dt').text(task.finish_dt_rus)

        tr.find('button[name=cancel]').prop('disabled', task.start_dt_rus)
        tr.find('button[name=restart]').prop('disabled', task.in_progress)

        if (task.result_attachment) {
            tr.find('.result-attachment-container').show()
            tr.find('.result-attachment').prop('href', task.result_attachment)
        } else {
            tr.find('.result-attachment-container').hide()
        }
    }

    function loadTasks() {
        let ids = $('tr').map(function () {
            $(this).data('task-id')
        }).toArray()

        let url = '/background_tasks/rest/task/'
        $.ajax({
            method: 'get',
            url: url,
            data: {
                id: ids,
            },
            traditional: true,
            success: function (response) {
                $(response).each(function (task) {
                    renderTask(task)
                })

                // периодически обновляем
                setTimeout(loadTasks, 2000)
            }
        })
    }

    prepareCancel()
    prepareRestart()
    loadTasks()
})
