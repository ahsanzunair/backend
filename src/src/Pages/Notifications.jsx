import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Notifications = () => {
    const navigate = useNavigate();

    const [notifications, setNotifications] = useState([
        {
            id: 1,
            title: "New Job Application",
            body:
                "A new candidate has applied for your Frontend Developer position. Please review the profile and take action.",
        },
        {
            id: 2,
            title: "Application Accepted",
            body:
                "Congratulations! Your application for the MERN Stack Developer role has been accepted by the company.",
        },
        {
            id: 3,
            title: "Job Expiring Soon",
            body:
                "Your posted job will expire in three days. Renew it to continue receiving applications from candidates.",
        },
    ]);

    const handleDelete = (id) => {
        setNotifications(notifications.filter((n) => n.id !== id));
    };

    return (
        <div className="max-w-4xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">Notifications</h1>

            {notifications.length === 0 && (
                <p className="text-gray-500 text-2xl font-bold">No Notifications Available</p>
            )}

            <div className="space-y-4">
                {notifications.map((n) => (
                    <div
                        key={n.id}
                        className="bg-white shadow rounded-lg p-4 flex flex-col sm:flex-row gap-5 sm:gap-0  justify-between items-center sm:items-start"
                    >
                        <div>
                            <h3 className="font-medium text-lg">{n.title}</h3>
                            <p className="text-gray-600 text-sm mt-1">
                                {n.body.split(" ").slice(0, 25).join(" ")}...
                            </p>
                        </div>

                        <div className="flex gap-2 ">
                            <button
                                onClick={() => navigate(`/notifications/${n.id}`, { state: n })}
                                className="px-3 py-1 text-lg bg-blue-500 text-white rounded-lg hover:bg-blue-600 cursor-pointer shadow-lg hover:shadow-2xl hover:scale-105 transform transition-all duration-300"
                            >
                                View
                            </button>

                            <button
                                onClick={() => handleDelete(n.id)}
                                className="px-3 py-1 text-lg bg-red-500 text-white rounded-lg hover:bg-red-600 cursor-pointer shadow-lg hover:shadow-2xl hover:scale-105 transform transition-all duration-300"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Notifications;
