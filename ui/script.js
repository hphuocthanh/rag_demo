document.getElementById('send-btn').addEventListener('click', function() {
  sendMessage();
});

document.getElementById('user-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
      sendMessage();
  }
});

function sendMessage() {
  const userInput = document.getElementById('user-input').value;
  if (userInput.trim() === '') return;

  // Append user message to chat box
  appendMessage('user-message', userInput);

  // Clear input
  document.getElementById('user-input').value = '';

  // Send the user input to the server
  fetch('http://localhost:5001/query', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: userInput })
  })
  .then(response => response.json())
  .then(data => {
      // Append bot response to chat box
      appendMessage('bot-message', data.result);
  })
  .catch(error => {
      console.error('Error:', error);
      appendMessage('bot-message', 'Error occurred, please try again.');
  });
}

function appendMessage(sender, message) {
  const chatBox = document.getElementById('chat-box');
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', sender);

  const messageContent = document.createElement('div');
  messageContent.classList.add('message-content');
  messageContent.innerText = message;

  messageElement.appendChild(messageContent);
  chatBox.appendChild(messageElement);

  // Scroll to the bottom of the chat box
  chatBox.scrollTop = chatBox.scrollHeight;
}
