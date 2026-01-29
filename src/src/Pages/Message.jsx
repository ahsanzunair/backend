import  { useState, useEffect, useRef } from "react";

export default function WhatsAppChat() {
    const [chats, setChats] = useState([
        {
            id: 1,
            company: "ECS Company",
            messages: [
                {
                    from: "them",
                    text: "Hello, we reviewed your profile and would like to discuss the project requirements with you."
                },
                {
                    from: "me",
                    text: "Thank you for reaching out. I am available to discuss the details at your convenience."
                },
                {
                    from: "them",
                    text: "Hello, we reviewed your profile and would like to discuss the project requirements with you."
                },
                {
                    from: "me",
                    text: "Thank you for reaching out. I am available to discuss the details at your convenience."
                },
                {
                    from: "them",
                    text: "Hello, we reviewed your profile and would like to discuss the project requirements with you."
                },
                {
                    from: "me",
                    text: "Thank you for reaching out. I am available to discuss the details at your convenience."
                },
                {
                    from: "them",
                    text: "Hello, we reviewed your profile and would like to discuss the project requirements with you."
                },
                {
                    from: "me",
                    text: "Thank you for reaching out. I am available to discuss the details at your convenience."
                },
            ]
        },
        {
            id: 2,
            company: "Software Pvt Ltd",
            messages: [
                {
                    from: "them",
                    text: "We have successfully received your application and it is currently under evaluation by our team."
                }
            ]
        },
        {
            id: 3,
            company: "TechNova Solutions",
            messages: [
                {
                    from: "them",
                    text: "Your technical assessment has been shortlisted. Our team would like to schedule a follow-up discussion."
                },
                {
                    from: "me",
                    text: "That sounds great. Please let me know the next steps and your preferred time."
                }
            ]
        }
    ]);

    const [selectedChatId, setSelectedChatId] = useState(null);
    const [showChat, setShowChat] = useState(false);
    const [input, setInput] = useState("");
    const bottomRef = useRef(null);

    const selectedChat = chats.find((c) => c.id === selectedChatId);

    const openChat = (id) => {
        setSelectedChatId(id);
        setShowChat(true);
    };

    const sendMessage = () => {
        if (!input.trim() || !selectedChat) return;

        setChats((prev) =>
            prev.map((chat) =>
                chat.id === selectedChatId
                    ? {
                        ...chat,
                        messages: [...chat.messages, { from: "me", text: input }]
                    }
                    : chat
            )
        );

        setInput("");
    };

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [selectedChat]);

    return (
        <div className="h-screen bg-white md:flex">


            <div
                className={`md:w-1/3 w-full  bg-white border-r ${showChat ? "hidden md:block" : "block"}`}
            >
                <div className="p-4 border-b">
                    <h2 className="text-2xl font-bold text-blue-600">Chats</h2>
                </div>

                <div className="overflow-auto px-5 py-2   h-[calc(100vh-80px)]">
                    {chats.map((chat) => (
                        <div
                            key={chat.id}
                            onClick={() => openChat(chat.id)}
                            className={`p-4 cursor-pointer border my-2 border-black rounded-lg hover:bg-gray-100 hover:scale-105 transform  transition-all duration-300 ${selectedChatId === chat.id ? "bg-gray-100" : ""
                                }`}
                        >
                            <p className="font-semibold text-gray-800">{chat.company}</p>
                            <p className="text-sm text-gray-500 truncate">
                                {chat.messages.at(-1)?.text}
                            </p>
                        </div>
                    ))}
                </div>
            </div>


            <div
                className={`md:w-2/3 w-full flex flex-col h-screen ${showChat ? "block" : "hidden md:flex"
                    }`}
            >
                {!selectedChat ? (
                    <div className="m-auto text-gray-600 text-xl font-medium">
                        Select a chat to start messaging
                    </div>
                ) : (
                    <>

                        <div className="flex-shrink:0 flex items-center gap-3 p-4 bg-white border-b shadow-sm">
                            <button
                                className="md:hidden text-xl"
                                onClick={() => setShowChat(false)}
                            >
                                ←
                            </button>
                            <h2 className="text-xl font-bold text-black">
                                {selectedChat.company}
                            </h2>
                        </div>


                        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                            {selectedChat.messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`max-w-[65%] px-4 py-2 rounded-xl shadow ${msg.from === "me"
                                        ? "bg-green-500 text-white ml-auto text-lg"
                                        : "bg-white text-black text-lg"
                                        }`}
                                >
                                    {msg.text}
                                </div>
                            ))}
                            <div ref={bottomRef} />
                        </div>


                        <div className="flex-shrink:0 p-4 bg-white border-t flex gap-3">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                                placeholder="Type a message"
                                className="flex-1 border rounded-full px-4 py-2 outline-none focus:ring-2 focus:ring-green-400"
                            />
                            <button
                                onClick={sendMessage}
                                className="bg-green-500 hover:bg-green-600 text-white px-6 rounded-full font-semibold shadow-lg transition"
                            >
                                Send
                            </button>
                        </div>
                    </>
                )}
            </div>

        </div>
    );
}
