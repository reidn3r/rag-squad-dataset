"use client";

import { useState, useRef } from "react";

export default function Home() {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [responses, setResponses] = useState<Array<{ query: string; response: string }>>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || isLoading) return;

    const userMessage = message;
    setMessage("");
    setIsLoading(true);

    const currentResponseIndex = responses.length;
    setResponses(prev => [...prev, { query: userMessage, response: "" }]);

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await fetch("http://localhost:8000/query/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userMessage }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("Failed to get reader from response");
      }

      let accumulatedResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              continue;
            }
            
            try {
              const parsed = JSON.parse(data);
              const content = parsed.content || parsed.data || data;
              
              accumulatedResponse += content;              
              setResponses(prev => {
                const newResponses = [...prev];
                if (newResponses[currentResponseIndex]) {
                  newResponses[currentResponseIndex].response = accumulatedResponse;
                }
                return newResponses;
              });
            } catch {
              accumulatedResponse += data;
              setResponses(prev => {
                const newResponses = [...prev];
                if (newResponses[currentResponseIndex]) {
                  newResponses[currentResponseIndex].response = accumulatedResponse;
                }
                return newResponses;
              });
            }
          }
        }
      }

      console.log(`Resposta completa para "${userMessage}":`, accumulatedResponse);

    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        console.log("Request cancelled");
      } else {
        console.error("Error sending message:", error);
        setResponses(prev => {
          const newResponses = [...prev];
          if (newResponses[currentResponseIndex]) {
            newResponses[currentResponseIndex].response = "Erro ao processar mensagem. Tente novamente.";
          }
          return newResponses;
        });
      }
    } finally {
      setIsLoading(false);
      if (abortControllerRef.current === abortController) {
        abortControllerRef.current = null;
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-black font-sans">
      <div className="border-b border-gray-800 p-4">
        <p className="text-gray-400 text-center text-sm mt-1">
          Respostas em tempo real via SSE
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {responses.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <p className="text-lg">💬 Nenhuma mensagem ainda</p>
              <p className="text-sm mt-2">Digite algo abaixo para começar</p>
            </div>
          </div>
        ) : (
          responses.map((item, index) => (
            <div key={index} className="space-y-2">
              {/* User Message */}
              <div className="flex justify-end">
                <div className="bg-blue-600 rounded-lg px-4 py-2 max-w-[70%]">
                  <p className="text-white">{item.query}</p>
                </div>
              </div>

              <div className="flex justify-start">
                <div className="bg-gray-800 rounded-lg px-4 py-2 max-w-[70%]">
                  {item.response ? (
                    <p className="text-gray-200 whitespace-pre-wrap">{item.response}</p>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}

        
      </div>

      <div className="border-t border-gray-800 p-4 bg-black">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Digite sua mensagem..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-gray-900 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              autoFocus
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Enviando...</span>
                </div>
              ) : (
                "Enviar"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}