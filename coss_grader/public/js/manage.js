/// <reference path="axios.js"/>
/// <reference path="jquery.js"/>
/// <reference path="semantic.js"/>
$('.ui.calendar').calendar({
    monthFirst: false,
    disableMinute: true,
    type: 'datetime',
    formatter: {
        datetime: function (date, settings) {
            if (!date) return '';
            var day = date.getDate();
            var month = date.getMonth() + 1;
            var year = date.getFullYear();
            var hour = date.getHours();
            var minute = date.getMinutes();
            var seconds = date.getSeconds()
            return day + '-' + month + '-' + year + " " + hour + ":" + minute + ":" + seconds;
        }
    }
});