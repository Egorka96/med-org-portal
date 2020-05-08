renderTask = (task)->
    # статус
    $('.task-status').text(task.status)

    # прогресс
    progress = $('.progress')
    if not task.start_dt or task.finish_dt
        progress.hide()

    else
        progress.show()
        progress.find('.progress-bar')
            .attr('aria-valuenow', task.percent)
            .css('width', "#{ task.percent }%")
            .text("#{ task.percent }%")

    $('.start-dt').text(task.start_dt_rus)
    $('.finish-dt').text(task.finish_dt_rus)

    $('button[name=cancel]').prop('disabled', task.start_dt_rus)
    $('button[name=restart]').prop('disabled', task.in_progress)

    if task.result_attachment
        $('.result-attachment').show()
        $('.result-attachment').prop('href', task.result_attachment)
    else
        $('.result-attachment').hide()

    $('#logs').load(window.location.href + ' #logs')


@loadTask = ->
    url = "/background_tasks/rest/task/#{ taskId }/"
    $.ajax({
        method: 'get'
        url: url
        success: (task) ->
            renderTask(task)

            setTimeout(loadTask, 1000)
    })


$ ->
    loadTask()