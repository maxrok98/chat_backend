document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {
        
        console.log("socket connected");
        // Each button should emit a "submit vote" event
        document.querySelector('#submit').onclick = () => {
                //let user = document.querySelector('#name').innerHTML;
                let chat_id = document.querySelector('#chat_id').innerHTML;
                let text = document.querySelector('#text').value;
                console.log(chat_id);
                socket.emit('send message', {'chat_id': parseInt(chat_id, 10), 'text': text});
                document.querySelector('#text').value = '';
                return false;
            };
        });

    // When a new vote is announced, add to the unordered list
    socket.on('return message', data => {
        let chat_id = document.querySelector('#chat_id').innerHTML;
        if (parseInt(data.chat_id) == parseInt(chat_id)) {
            const li = document.createElement('li');
            li.innerHTML = `${data.user}: ${data.text}`;
            document.querySelector('#votes').append(li);
        }
    });
});
