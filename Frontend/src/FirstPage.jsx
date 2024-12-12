import { useState, useEffect } from "react";
import { AiOutlineSend } from "react-icons/ai"; // React Icon for the send button
import { ImSpinner8 } from "react-icons/im"; // React Icon for loading spinner
import "./FirstPage.css";

const FirstPage = () => {
    const [input, setInput] = useState("");
    const [status, setStatus] = useState("idle"); // idle | loading | success
    const [result, setResult] = useState("")
    const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Establish WebSocket connection
    const ws = new WebSocket("ws://localhost:8080"); // Replace with your WebSocket server URL
    setSocket(ws);

    ws.onopen = () => {
      console.log("WebSocket connection established.");
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    // Cleanup on component unmount
    return () => {
      ws.close();
      console.log("Webdocket closed")
    };
  }, []);

  useEffect(() => {
    if (!socket) return;

    // Handle messages from the WebSocket server
    socket.onmessage = (event) => {
      const response = event.data; // Assuming the server sends plain text
      setResult(response);
      setStatus("success");
    };
  }, [socket]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || !socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    setStatus("loading");
    setResult(""); // Clear previous result

    // Send message to the WebSocket server
    socket.send(input);
  };


  return (
    <div className="agentic-flow-wrapper">
      <div className="agentic-flow-container">
        <header className="header">
          <h1>Ask the AI</h1>
          <p>Your professional assistant is here to help.</p>
        </header>

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="input-box"
            disabled={status === "loading"}
          />
          <button
            type="submit"
            className="send-button"
            disabled={status === "loading"}
          >
            {status === "loading" ? <ImSpinner8 className="spinner" /> : <AiOutlineSend />}
          </button>
        </form>
      </div>
          <div className="result-container">
            {status === "success" ? (
                <div className="result">{result}</div>
            ) : <div className="result">Loading...</div>}

        </div>
    </div>
  );
};

export default FirstPage;
