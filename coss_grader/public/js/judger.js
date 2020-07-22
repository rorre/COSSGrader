/// <reference path="axios.js"/>
/// <reference path="jquery.js"/>
/// <reference path="semantic.js"/>
const play_id = $("#play_id").val()

$("#donebtn").click(function () {
    $('body').toast({
        title: 'Uploading...',
    })

    const data = { scores: generateScoreArray() }
    axios.post(`/api/play/${play_id}/set`, data).then(function () {
        $('body').toast({
            title: "Done!",
            message: "Heading back to home..."
        })
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

function generateScoreArray() {
    var scores = []
    $("form").each(function () {
        const $this = $(this)
        const score = Number($this.find('input[name="score"]')[0].value)
        scores.push(score)
    })
    console.log(scores)
    return scores
}

$(".qnum").click(function () {
    $.tab('change tab', $(this).data("tab"))
})

$('.ui.radio.checkbox').checkbox()

$(function () {
    $("form").each(function () {
        const $this = $(this)
        const score = Number($this.find('input[name="score"]')[0].value)
        const i = $this.data("tab")
        switch (score) {
            case 1:
                $(".qnum[data-tab='" + i + "']").addClass("green")
                break
            case 0:
                $(".qnum[data-tab='" + i + "']").addClass("red")
                break
        }
    })
})