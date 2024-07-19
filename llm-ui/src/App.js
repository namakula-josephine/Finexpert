import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaperPlane } from '@fortawesome/free-solid-svg-icons';

function App() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);

    const handleQuery = async () => {
        if (!query) return;

        const newMessages = [...messages, { text: query, sender: 'user' }];
        setMessages(newMessages);
        setQuery('');

        try {
            const result = await axios.post('http://127.0.0.1:5000/query', { query });
            setMessages([...newMessages, { text: result.data.answer, sender: 'bot' }]);
        } catch (error) {
            console.error("Error fetching the response:", error);
            setMessages([...newMessages, { text: "An error occurred while fetching the response.", sender: 'bot' }]);
        }
    };

    const handleNewChat = () => {
        setMessages([]);
        setQuery('');
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleQuery();
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>FINEXPERTAI</h1>
                <button className="new-chat-button" onClick={handleNewChat}>New Chat</button>
                <div className="chat-window">
                    {messages.map((msg, index) => (
                        <div key={index} className={`chat-bubble ${msg.sender}`}>
                            {msg.text}
                        </div>
                    ))}
                </div>
                <div className="input-area">
                    <textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Enter your query here"
                        rows="2"
                    />
                    <FontAwesomeIcon
                        icon={faPaperPlane}
                        className="send-icon"
                        onClick={handleQuery}
                    />
                </div>
            </header>
        </div>
    );
}

export default App;
