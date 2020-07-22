/// <reference path="axios.js"/>
/// <reference path="jquery.js"/>
/// <reference path="semantic.js"/>
// TODO: make these consts gone or better

const new_quiz = `
<form class="ui segment">
    <div class="ui form">
        <div class="field">
            <label>Question</label>
            <textarea name="question"></textarea>
        </div>
        <div class="ui info message">
            <p>Markdown styling is supported.</p>
        </div>
    </div>

    <div class="ui divider"></div>
    <div class="ui toggle checkbox">
        <input type="checkbox" name="is_essay">
        <label>Answer is in form of essay.</label>
    </div>
    <div class="ui divider"></div>
    <div class="answer-editor"></div>
</form>
`

const new_button = `
<div class="item">
    <button class="ui button qnum"></button>
</div>
`

const multiple_html = `
<div class="ui form">
    <div class="field">
        <div class="ui radio checkbox">
            <input type="radio" name="answer" value="0">
            <label><div class="ui input">
                <input type="text" name="opt-0" placeholder="Jawaban">
            </div></label>
        </div>
    </div>
    <div class="field">
        <div class="ui radio checkbox">
            <input type="radio" name="answer" value="1">
            <label><div class="ui input">
                <input type="text" name="opt-1" placeholder="Jawaban">
            </div></label>
        </div>
    </div>
    <div class="field">
        <div class="ui radio checkbox">
            <input type="radio" name="answer" value="2">
            <label><div class="ui input">
                <input type="text" name="opt-2" placeholder="Jawaban">
            </div></label>
        </div>
    </div>
    <div class="field">
        <div class="ui radio checkbox">
            <input type="radio" name="answer" value="3">
            <label><div class="ui input">
                <input type="text" name="opt-3" placeholder="Jawaban">
            </div></label>
        </div>
    </div>
    <div class="field">
        <div class="ui radio checkbox">
            <input type="radio" name="answer" value="4">
            <label><div class="ui input">
                <input type="text" name="opt-4" placeholder="Jawaban">
            </div></label>
        </div>
    </div>
</div>
`

const essay_html = `
<div class="ui form">
    <div class="field">
        <label>Answer</label>
        <textarea name="answer"></textarea>
    </div>
</div>
`

$("#addbtn").click(function () {
    // Decide new quiz tab ID based on the length of the questions array.
    // IDs will always be 0-indexed.
    const $questions = $("#q-numbers")
    var i = $questions.children().length

    const $quiz = $(new_quiz)
    const $answer_editor = $quiz.children(".answer-editor")

    $quiz.attr("id", `q-${i}`)
    $quiz.find("input").click(on_toggle)
    $answer_editor.attr("id", `aq-${i}`)
    $quiz.hide()

    // By default, it should show multiple choice answer.
    show_multiple($answer_editor)
    $("#questions").append($quiz)

    // Add the button to the tabs.
    const $button = $(new_button)
    $button.data("tab", i)
    $button.children("button").html(i + 1)
    $button.click(on_question_click)
    $questions.append($button)
})

$(".qnum").click(on_question_click)

function on_question_click() {
    const $this = $(this)
    var i = $this.data("tab")
    hide($(".visible"))
    show($(`#q-${i}`))
}

function on_toggle() {
    const $this = $(this)
    const answer_id = $($this.parents()[1]).attr("id")
    const $answer_panel = $(`#a${answer_id}`)
    if ($this.is(':checked')) {
        show_essay($answer_panel)
    } else {
        show_multiple($answer_panel)
    }
}

$("#delbtn").click(function () {
    const $visible_form = $(".visible")
    if (!$visible_form.length) {
        $('body').toast({
            class: 'error',
            title: `Error`,
            message: "Currently not viewing any question."
        })
        return
    }

    const q_id = Number($visible_form.attr("id").split("-")[1])
    var forms = $("form")
    var buttons = $(".qnum")
    $(forms[q_id]).remove()
    $(buttons[q_id]).parent().remove()
    for (var i = q_id + 1; i < forms.length; i++) {
        var $current = $(forms[i])
        $current.attr("id", `q-${i - 1}`)
        $current.children(".answer-editor").attr("id", `aq-${i - 1}`)

        var $current_button = $(buttons[i]).parent()
        $current_button.data("tab", i - 1)
        $current_button.children("button").html(i)
    }
})

$("#donebtn").click(function () {
    // Metadata //
    const $metadata_form = $("#metadata_form")
    const title = $metadata_form.find('input[name="title"]')[0].value || "No title"
    const info = $metadata_form.find('textarea[name="info"]')[0].value || ""

    // Question //
    var questions = []
    $("form").each(function (i) {
        console.log(`Serializing form ${i}`)
        questions.push(serializeForm($(this), i))
    })
    const data = {
        title: title,
        info: info,
        questions: questions
    }

    // POST //
    $('body').toast({
        title: 'Creating...',
        message: "Creating new quiz..."
    })
    axios.post("/api/quiz/new", data).then(function (response) {
        $('body').toast({
            title: "Done!",
            message: "Heading back to quiz listing..."
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

// ----------------
// Helper functions
// ----------------

function show_error(message, i) {
    $('body').toast({
        class: 'error',
        title: `Error in question #${i + 1}`,
        message: message
    })
}

function hide($elem) {
    $elem.removeClass("visible")
    $elem.hide()
}

function show($elem) {
    $elem.addClass("visible")
    $elem.show()
}

function show_essay($elem) {
    $elem.empty()
    $elem.html(essay_html)
}

function show_multiple($elem) {
    $elem.empty()
    $elem.html(multiple_html)
}

function serializeForm($form, i) {
    var question = $form.find('textarea[name="question"]')[0].value
    if (!question) {
        show_error("No question provided.", i)
        return
    }

    var is_essay = $form.find('input[name="is_essay"]')[0].checked
    var answer, options;

    if (is_essay) {
        answer = $form.find('textarea[name="answer"]')[0].value
        if (!answer) {
            show_error(`Missing answer.`, i)
            return
        }
    } else {
        var $checked_radio = $form.find('input[type="radio"]:checked')
        if (!$checked_radio.length) {
            show_error("No option selected.", i)
            return
        }
        answer = $checked_radio[0].value
        var options = []
        $form.find('input[placeholder="Jawaban"]').each(function (i) {
            opt = $(this).val()
            if (!opt) {
                show_error(`Missing answer for index ${i + 1}.`, i)
                return
            }
            options.push(opt)
        })
    }
    return {
        question: question,
        is_essay: Boolean(is_essay),
        answer: answer,
        options: options
    }
}