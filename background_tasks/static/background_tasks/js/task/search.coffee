
prepareCancel = ->
    $('button[name=cancel]').click ->
        taskId = $(this).val()

        $.ajax({
            url: "/background_tasks/rest/task/#{taskId}/cancel/",
            method: 'put'
            success: ->
                $.toast({
                    heading: ''
                    text: 'Задача отменена'
                    icon: 'info'
                    showHideTransition: 'fade'
                    stack: 1
                    position: 'top-right'
                })
        }).fail(->
            $.toast({
                heading: ''
                text: 'Ошибка отмены задачи'
                icon: 'error'
                showHideTransition: 'fade'
                stack: 1
                position: 'top-right'
            })
        )


prepareRestart = ->
    $('button[name=restart]').click ->
        taskId = $(this).val()

        $.ajax({
            url: "/background_tasks/rest/task/#{taskId}/restart/",
            method: 'put'
            success: ->
                $.toast({
                    heading: ''
                    text: 'Задача перезапущена'
                    icon: 'info'
                    showHideTransition: 'fade'
                    stack: 1
                    position: 'top-right'
                })
        }).fail(->
            $.toast({
                heading: ''
                text: 'Ошибка перезапуска задачи'
                icon: 'error'
                showHideTransition: 'fade'
                stack: 1
                position: 'top-right'
            })
        )


renderTask = (task)->
    tr = $("#task_#{ task.id }")

    # статус
    tr.removeClass('success').removeClass('danger')
    if task.is_success
        tr.addClass('success')
    if task.is_fail
        tr.addClass('danger')

    # прогресс
    progress = tr.find('.progress')
    if not task.start_dt or task.finish_dt
        progress.hide()
        tr.find('.task-status').text(task.status).show()
    else
        tr.find('.task-status').text(task.status).hide()
        progress.show()
        progress.find('.progress-bar')
            .attr('aria-valuenow', task.percent)
            .css('width', "#{ task.percent }%")
            .text("#{ task.percent }%")

    tr.find('.start-dt').text(task.start_dt_rus)
    tr.find('.finish-dt').text(task.finish_dt_rus)

    tr.find('button[name=cancel]').prop('disabled', task.start_dt_rus)
    tr.find('button[name=restart]').prop('disabled', task.in_progress)

    if task.result_attachment
        tr.find('.result-attachment-container').show()
        tr.find('.result-attachment').prop('href', task.result_attachment)
    else
        tr.find('.result-attachment-container').hide()


@loadTasks = ->
    ids = $('tr').map(-> $(this).data('task-id')).toArray()
    url = '/background_tasks/rest/task/'
    $.ajax({
        method: 'get'
        url: url
        data:
            id: ids
        traditional: true
        success: (response) ->
            for task in response
                renderTask(task)

            # периодически обновляем
            setTimeout(loadTasks, 2000)
    })

$ ->
    prepareCancel()
    prepareRestart()
    loadTasks()