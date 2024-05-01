document.getElementById('dl-btn').addEventListener('click', function() {
    sendMessage('DL');
});

document.getElementById('rc-btn').addEventListener('click', function() {
    sendMessage('RC');
});
document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});
document.getElementById('clear-btn').addEventListener('click', function() {
    clearLogs();
    document.getElementById('user-input').value = '';
});
document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function clearLogs() {
    const logContainer = document.getElementById('chat-log');
    const laterLogs = Array.from(logContainer.children).slice(2);
    laterLogs.forEach(log => log.remove());
    fetch('/clear-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }, 
        body: JSON.stringify({ conversation_stage: true }),  
    })
}

function sendMessage(option) {
    let userInput = document.getElementById('user-input').value.trim();
    if (option) {
        userInput = option;  
    }
    if (userInput !== '') {
        appendMessage('You', userInput);
        document.getElementById('user-input').value = '';
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_input: userInput }),  
        })
        .then(response => response.json())
        .then(data => {
            appendMessage('Assistant', data.response);
        })
        .catch(error => console.error('Error:', error));
    }
}

function appendMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    if (sender === 'You') {
        messageElement.classList.add('user-message');
    } else if (sender === 'Assistant') {
        messageElement.classList.add('bot-message');
    }
    
    document.getElementById('chat-log').appendChild(messageElement);
    document.getElementById('chat-log').scrollTop = document.getElementById('chat-log').scrollHeight;

    
}

