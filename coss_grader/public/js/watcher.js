/// <reference path="axios.js"/>
/// <reference path="jquery.js"/>
/// <reference path="semantic.js"/>
// Visibility API
var browserPrefixes = ['moz', 'ms', 'o', 'webkit'],
    isVisible = true; // internal flag, defaults to true

// get the correct attribute name
function getHiddenPropertyName(prefix) {
    return (prefix ? prefix + 'Hidden' : 'hidden')
}

// get the correct event name
function getVisibilityEvent(prefix) {
    return (prefix ? prefix : '') + 'visibilitychange'
}

// get current browser vendor prefix
function getBrowserPrefix() {
    for (var i = 0; i < browserPrefixes.length; i++) {
        if (getHiddenPropertyName(browserPrefixes[i]) in document) {
            // return vendor prefix
            return browserPrefixes[i];
        }
    }

    // no vendor prefix needed
    return null;
}

// bind and handle events
var browserPrefix = getBrowserPrefix(),
    hiddenPropertyName = getHiddenPropertyName(browserPrefix),
    visibilityEventName = getVisibilityEvent(browserPrefix);

function onVisible() {
    // prevent double execution
    if (isVisible) return

    // change flag value
    isVisible = true
    reportEvent("Player is looking at quiz now.")
}

function onHidden() {
    // prevent double execution
    if (!isVisible) return


    // change flag value
    isVisible = false
    reportEvent("Player has left quiz tab.")
}

function handleVisibilityChange(forcedFlag) {
    // forcedFlag is a boolean when this event handler is triggered by a
    // focus or blur eventotherwise it's an Event object
    if (typeof forcedFlag === "boolean") {
        if (forcedFlag) {
            return onVisible();
        }

        return onHidden();
    }

    if (document[hiddenPropertyName]) {
        return onHidden();
    }

    return onVisible();
}

function startVisibilityWatch() {
    console.log("INFO: Register event handlers for visibility.")
    document.addEventListener(visibilityEventName, handleVisibilityChange, false);

    // extra event listeners for better behaviour
    // Disabled for now as it is deemed too sensitive
    /*
    document.addEventListener('focus', function () {
        handleVisibilityChange(true);
    }, false);

    document.addEventListener('blur', function () {
        handleVisibilityChange(false);
    }, false);

    window.addEventListener('focus', function () {
        handleVisibilityChange(true);
    }, false);

    window.addEventListener('blur', function () {
        handleVisibilityChange(false);
    }, false);
    */
}

// Logger
function reportEvent(s) {
    console.log("INFO: Logging '" + s + "'")
    axios.post(`/api/play/${play_id}/report`, { data: s }).then(function () {
        console.log("INFO: Logged")
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
    })
}

// ---------
$(function () {
    reportEvent("Player starts quiz.")
    startVisibilityWatch()
})