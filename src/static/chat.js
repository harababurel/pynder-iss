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
        this.autoScrool = true;
        this.active = false;
        this.timer = null;
        this.updateRequest();
    }

    updateScroll() {
        if (this.autoScrool) {
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
                if (thisClass.autoScrool)
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
                if (thisClass.autoScrool)
                    thisClass.updateScroll();
                if(data.responseText !== "")
                    this;// TODO notification
                else
                    thisClass.timer = setTimeout(thisClass.updateRequest.bind(thisClass), ACTIVE_REQUEST_INTERVAL);
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
        if (activeChat != null)
            activeChat.active = false;
        activeChat = null;
        $('#chat-div > ul').empty();
    })
});
$('#send-message').submit(function (e) {
    console.log(e);
    $.ajax({
           type: 'POST',
           url: '/chat/' + activeChat.matchId,
           data: $("#send-message").serialize(), // serializes the form's elements.
           success: function(data)
           {
           }
         });
    e.preventDefault();
});