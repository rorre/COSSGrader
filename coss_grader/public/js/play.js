/// <reference path="axios.js"/>
/// <reference path="jquery.js"/>
/// <reference path="semantic.js"/>
var answers = []
const play_id = $("#play_id").val()

$(function () {
    // Fill in with blank answers
    for (var i = 0; i < $("#q-numbers").children().length; i++) {
        answers.push("")
    }
    $('.ui.radio.checkbox').checkbox()
})


$("#donebtn").click(function () {
    $('body').toast({
        title: 'Uploading...',
    })

    const data = { answers: generateAnswerArray() }
    axios.post(`/api/play/${play_id}/finish`, data).then(function () {
        $('body').toast({
            title: "Done!",
            message: "Heading back to home..."
        })
        clearInterval(autosave)
        window.location.href = '/'
    }).catch(function (error) {
        if (error.response) {
            if (400 < error.response.status < 500) {
                $('body').toast({
                    class: 'error',
                    title: 'Error',
                    message: error.response.data.err
                })
            } else if (error.response.status >= 500) {
                $('body').toast({
                    class: 'error',
                    title: 'Error',
                    message: "A server error has occured."
                })
            }
        } else {
            $('body').toast({
                class: 'error',
                title: 'Error',
                message: "An error has occured. " + error.message
            })
        }
    })
})

$(".qnum").click(function () {
    $.tab('change tab', $(this).data("tab"))
})

// Autosave timer
var autosave = setInterval(function () {
    var current_answers = generateAnswerArray()
    var data = { answers: current_answers }
    console.log("INFO: Performing autosave")
    axios.post(`/api/play/${play_id}/save`, data).then(function () {
        console.log("INFO: Autosave done")
    }).catch(function (error) {
        if (error.response) {
            if (400 < error.response.status < 500) {
                console.log("ERROR: " + error.response.data.err)
            } else if (error.response.status >= 500) {
                console.log("ERROR: Server returns 5xx")
            }
        } else {
            console.log("ERROR: " + error.message)
        }
    })
}, 20000)

// COUNTDOWN
var $countdown = $("#countdown")
var countdown = setInterval(function () {
    var seconds_left = Number($countdown.data("time-left"))
    const HOUR = 60 * 60
    const MINUTE = 60

    var hours = Math.floor(seconds_left / HOUR);
    var minutes = Math.floor(seconds_left % HOUR / MINUTE)
    var seconds = Math.floor(seconds_left % MINUTE)

    $countdown.html(`${hours}:${minutes}:${seconds}`)
    if (seconds_left < 0) {
        clearInterval(countdown)
        alert("Timed out.")
        $("#donebtn").click()
    }
    $countdown.data("time-left", seconds_left - 1)

}, 1000)

// HELPER
function generateAnswerArray() {
    $("form").each(function () {
        var answer = ""

        const $this = $(this)
        const i = $this.data("tab")
        const is_essay = $this.find('input[name="is_essay"').val() == "True"

        if (is_essay) {
            answer = $this.find("textarea").val()
        } else {
            var selected_opt = $this.find('input[type="radio"]:checked')
            if (!selected_opt.length) {
                answer = ""
            } else {
                answer = selected_opt[0].value
            }
        }
        answers[i] = answer
    })
    console.log(answers)
    return answers
}