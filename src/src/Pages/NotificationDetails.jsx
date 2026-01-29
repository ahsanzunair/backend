import { useLocation, useNavigate } from "react-router-dom";

const NotificationDetail = () => {
    const { state } = useLocation();
    const navigate = useNavigate();

    if (!state) {
        return (
            <p className="text-center mt-10 text-gray-500">
                Notification not found
            </p>
        );
    }

    return (
        <div className="max-w-3xl mx-auto p-4">
            <button
                onClick={() => navigate(-1)}
                className="mb-4 bg-blue-500 text-2xl text-white px-2 py-1 rounded-lg cursor-pointer shadow-lg hover:shadow-2xs hover:scale-105 transform transition-all duration-300 "
            >
                ← Back
            </button>

            <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-2xl font-semibold mb-4">
                    {state.title}
                </h2>
                <p className="text-gray-700 leading-relaxed">
                    {state.body}
                </p>
            </div>
        </div>
    );
};

export default NotificationDetail;
