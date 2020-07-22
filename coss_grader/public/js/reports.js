/// <reference path="axios.js"/>
/// <reference path="jquery.js"/>
/// <reference path="semantic.js"/>
/// <reference path="jquery.timeago.js"/>
$(function () {
    $.timeago.settings.allowFuture = true;
    $(".timeago").timeago()
})

const quiz_id = $("#quiz_id").val()
const $table_body = $("tbody")
var x = setInterval(function () {
    var last_id = -1
    $("tr").each(function () {
        const $this = $(this)
        const id = Number($this.data("id"))
        if (last_id < id) {
            last_id = id
        }
    })
    console.log("INFO: last_id = " + last_id)

    console.log("INFO: Fetching data...")
    axios.get(`/api/quiz/${quiz_id}/reports`).then(function (response) {
        for (var i = 0; i < response.data.length; i++) {
            var event = response.data[i]
            if (event.id == last_id) return;

            const row = $(`<tr data-id="${event.id}">
                            <td><time class="timeago" datetime="${event.datetime}"></time></td>
                            <td>${event.name}</td>
                            <td>${event.event}</td>
                        </tr>`)
            $table_body.prepend(row)
        }
    }).catch(function (error) {
        if (error.response) {
            if (400 < error.response.status < 500) {
                console.log("ERROR: " + error.response.data.err)
            } else if (error.response.status >= 500) {
                console.log("ERROR: Server returned 5xx code.")
            }
        } else {
            console.log("ERROR: " + error.message)
        }
    }).finally(function () {
        $(".timeago").timeago()
    })
}, 10000)