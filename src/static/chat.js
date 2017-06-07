/**
 * Created by heghe on 6/6/17.
 */

const REQUEST_INTERVAL = 10000; // 1000 = 1 second
const ACTIVE_REQUEST_INTERVAL = 1000;

let activeChat = null;
let chats = [];

class chat {
    constructor(matchId) {
        this.matchId = matchId;
        this.totalMessages = 0;
        this.autoScroll = true;
        this.active = false;
        this.timer = null;
        this.notified = null;
        this.updateRequest();
    }

    updateScroll() {
        if (this.autoScroll) {
            let element = document.getElementById('chat-div');
            element.scrollTop = element.scrollHeight;
        }
    }

    updateRequest() {
        if (this.active)
            this.updateMessages();
        else
            this.notificationMessage();
    }

    updateMessages() {
        this.totalMessages = $('#chat-div > ul li').length;
        let thisClass = this;
        $.ajax({
            type: 'POST',
            url: '/messages',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({
                active: thisClass.active,
                messageNumber: thisClass.totalMessages,
                match: thisClass.matchId
            }),
            complete: function (data) {
                $('#chat-div > ul').append(data.responseText);
                if (thisClass.autoScroll)
                    thisClass.updateScroll();
                thisClass.timer = setTimeout(thisClass.updateRequest.bind(thisClass), ACTIVE_REQUEST_INTERVAL);
            }
        });
    }

    notificationMessage() {
        let thisClass = this;
        $.ajax({
            type: 'POST',
            url: '/messages',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({
                active: thisClass.active,
                messageNumber: thisClass.totalMessages,
                match: thisClass.matchId
            }),
            complete: function (data) {
                if (thisClass.autoScroll)
                    thisClass.updateScroll();
                if (data.responseText !== "" && !thisClass.notified) {
                    thisClass.notified = true;
                    $('#title' + thisClass.matchId).append('<span class="label label-primary notification" style="float: right; margin-right: 5px">New message</span>');
                }
                if (!thisClass.notified)
                    thisClass.timer = setTimeout(thisClass.updateRequest.bind(thisClass), REQUEST_INTERVAL);
            }
        });
    }
}
function openChat(userId) {
    $('#chat-div').collapse('show'); //activate chat and reset messages
    for (let _chat of chats) {
        if (_chat.matchId === userId) {
            activeChat = _chat;
            activeChat.active = true;
            $('#title' + activeChat.matchId + ' > .notification').remove();
            clearTimeout(activeChat.timer);
            activeChat.updateRequest();
            break
        }
    }
}

$('document').ready(function () {
    $('#profile-div').children('.collapse').each(function () {
        if ($(this).attr('id') !== 'chat-div') {
            let _chat = new chat($(this).attr('id'));
            chats.push(_chat);
        }
    });
    console.log(chats.length);
});
$(function () {
    $('.div-match').click(function () {
        if (activeChat != null) {
            clearTimeout(activeChat.timer);
            activeChat.active = false;
            activeChat.notified = false;
            activeChat.timer = setTimeout(activeChat.updateRequest.bind(activeChat), REQUEST_INTERVAL);
            activeChat = null;
        }
        $('#chat-div > ul').empty();
        $('#chat-div').collapse('hide');
    })
});
$('#send-message').submit(function (e) {
    $.ajax({
        type: 'POST',
        url: '/chat/' + activeChat.matchId,
        data: $("#send-message").serialize(), // serializes the form's elements.
        success: function (data) {
        }
    });
    $('#send-message')[0].reset();
    e.preventDefault();
});

$('#chat-div').on('scroll', function () {
    let element = document.getElementById('chat-div');
    console.log(element.scrollHeight, element.scrollTop, activeChat.autoScroll);
    if (element.scrollTop != element.scrollHeight)
        activeChat.autoScroll = false;
    if (element.scrollHeight - element.scrollTop <= 570)
        activeChat.autoScroll = true;
});