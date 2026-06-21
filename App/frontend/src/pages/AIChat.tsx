import { useState } from "react";
import { Bot, Send, Trash2, User } from "lucide-react";
import { askAI } from "../services/chatApi";

type Message = {
  role: "user" | "assistant";
  text: string;
};

export default function AIChat() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState<Message[]>([]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userText = message;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: userText,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const res = await askAI(userText);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.response,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Không thể kết nối tới MediPredict AI.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">

      {/* Header */}

      <div className="mb-8">

        <h1 className="text-4xl font-bold text-blue-700">

          🩺 MediPredict AI

        </h1>

        <p className="text-slate-500 mt-2">

          Trợ lý sức khỏe thông minh.

        </p>

      </div>

      {/* Chat box */}

      <div className="bg-white rounded-3xl shadow-xl border border-slate-200 h-[600px] flex flex-col">

        {/* Toolbar */}

        <div className="border-b border-slate-200 p-4 flex justify-between items-center">

          <div className="flex items-center gap-3">

            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">

              <Bot className="h-5 w-5 text-blue-600" />

            </div>

            <div>

              <h3 className="font-semibold text-slate-800">

                MediPredict AI

              </h3>

              <p className="text-xs text-green-600">

                ● Đang hoạt động

              </p>

            </div>

          </div>

          <button

            onClick={() => setMessages([])}

            className="flex items-center gap-2 text-red-500 hover:bg-red-50 px-3 py-2 rounded-lg transition"

          >

            <Trash2 className="h-4 w-4" />

            Xóa

          </button>

        </div>

        {/* Nội dung chat */}

        <div className="flex-1 overflow-y-auto p-6 bg-slate-50">

          {messages.length === 0 && (

            <div className="text-center text-slate-500 mt-20">

              <h3 className="font-semibold text-xl mb-5">

                💡 Bạn có thể hỏi:

              </h3>

              <div className="space-y-3">

                <p>🩺 Tôi bị đau họng và sốt nhẹ</p>

                <p>💊 Vitamin C dùng thế nào?</p>

                <p>🍎 Người thiếu máu nên ăn gì?</p>

                <p>🏃 Làm sao ngủ ngon hơn?</p>

              </div>

            </div>

          )}

          {messages.map((m, i) => (

            <div

              key={i}

              className={`flex mb-5 ${
                m.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}

            >

              <div

                className={`
                  max-w-[80%]
                  rounded-2xl
                  px-5
                  py-4
                  shadow-sm
                  ${
                    m.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white text-slate-800 border border-slate-200"
                  }
                `}

              >

                <div className="flex items-center gap-2 mb-2">

                  {m.role === "user" ? (

                    <User className="h-4 w-4" />

                  ) : (

                    <Bot className="h-4 w-4 text-blue-600" />

                  )}

                  <b>

                    {m.role === "user"

                      ? "Bạn"

                      : "MediPredict"}

                  </b>

                </div>

                <p className="whitespace-pre-wrap">

                  {m.text}

                </p>

              </div>

            </div>

          ))}

          {loading && (

            <div className="text-slate-500">

              🤖 MediPredict đang trả lời...

            </div>

          )}

        </div>

        {/* Input */}

        <div className="border-t border-slate-200 p-4">

          <div className="flex gap-3">

            <input

              className="
              flex-1
              border
              border-slate-300
              rounded-xl
              px-5
              py-3
              text-slate-800
              placeholder:text-slate-400
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              "

              placeholder="Hỏi MediPredict AI..."

              value={message}

              onChange={(e) => setMessage(e.target.value)}

              onKeyDown={(e) => {

                if (e.key === "Enter") {

                  sendMessage();

                }

              }}

            />

            <button

              onClick={sendMessage}

              className="
              bg-blue-600
              hover:bg-blue-700
              text-white
              px-6
              rounded-xl
              flex
              items-center
              gap-2
              transition
              "

            >

              <Send className="h-4 w-4" />

              Gửi

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}