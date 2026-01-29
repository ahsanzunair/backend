import { useState } from "react";
import { FaUserCircle } from "react-icons/fa";
import { toast } from "react-toastify";
import ppp from "../assets/profile_img_3.png"

const Profile = () => {

    const [user, setUser] = useState({
        fullName: "Haris Zeeshan",
        email: "haris@example.com",
        phone: "03021234567",
        city: "Lahore",
        skills: ["React", "Node.js", "Tailwind"],
        role: "JobSeeker",
        resumeLink: "https://example.com/resume.pdf",
        avatarUrl: ppp
    });

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [formData, setFormData] = useState({ ...user });


    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };


    const handleSubmit = (e) => {
        e.preventDefault();
        setUser(formData);
        setIsModalOpen(false);
    };

    return (
        <div className="max-w-4xl mx-auto p-6 px-10 bg-white rounded-lg shadow-lg mt-10" >

            < div className="flex flex-col sm:flex-row items-center gap-6 mb-6" >
                {
                    user.avatarUrl ? (
                        <img
                            src={user.avatarUrl}
                            alt="Avatar"
                            className="w-28 h-28 rounded-full object-cover border-2 border-gray-300"
                        />
                    ) : (
                        <FaUserCircle className="w-28 h-28 text-gray-400" />
                    )
                }

                < div >
                    <h1 className="text-2xl font-semibold text-gray-800">{user.fullName}</h1>
                </div >
            </div >


            < div className="grid grid-cols-1 sm:grid-cols-2  gap-4 mb-6" >
                <div className="flex items-center  justify-start gap-1">
                    <p className="text-black font-bold  ">Email:</p>
                    <p className="text-gray-900 font-medium">{user.email}</p>
                </div>
                <div className="flex items-center  justify-start gap-1">
                    <p className="text-black font-bold">Phone:</p>
                    <p className="text-gray-900 font-medium">{user.phone}</p>
                </div>
                <div className="flex items-center  justify-start gap-1">
                    <p className="text-black font-bold">City:</p>
                    <p className="text-gray-900 font-medium">{user.city}</p>
                </div>
                <div className="flex items-center  justify-start gap-1">
                    <p className="text-black font-bold">Role:</p>
                    <p className="text-gray-900 font-medium">{user.role}</p>
                </div>
                <div className="flex items-center  justify-start gap-1">
                    <p className="text-black font-bold">Skills:</p>
                    <p className="text-gray-900 font-medium">{user.skills.join(", ")}</p>
                </div>
                <div className="flex items-center  justify-start gap-1">
                    <p className="text-black font-bold">Resume:</p>
                    <a
                        href={user.resumeLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                    >
                        View Resume
                    </a>
                </div>
            </div >


            < button
                onClick={() => setIsModalOpen(true)}
                className=" flex items-center justify-center sm:justify-start px-6 py-2 bg-blue-500 text-white rounded-lg  hover:bg-blue-600 transition-colors duration-300 "
            >
                Edit Profile
            </button >



            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-transparent bg-opacity-30 backdrop-blur-xs">
                    <div className="bg-white rounded-2xl w-full max-w-lg p-8 shadow-xl transform transition-all scale-95 animate-fade-in">
                        <h2 className="text-2xl font-semibold mb-6 text-gray-800">Edit Profile</h2>

                        <form onSubmit={handleSubmit} className="space-y-5 max-h-[80vh] overflow-y-auto">

                            <div>
                                <label className="block text-gray-600 mb-1 font-medium">Full Name</label>
                                <input
                                    type="text"
                                    name="fullName"
                                    value={formData.fullName}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                                    required
                                />
                            </div>


                            <div>
                                <label className="block text-gray-600 mb-1 font-medium">Email</label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                                    required
                                />
                            </div>


                            <div>
                                <label className="block text-gray-600 mb-1 font-medium">Phone</label>
                                <input
                                    type="text"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                                />
                            </div>


                            <div>
                                <label className="block text-gray-600 mb-1 font-medium">City</label>
                                <input
                                    type="text"
                                    name="city"
                                    value={formData.city}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                                />
                            </div>


                            <div>
                                <label className="block text-gray-600 mb-1 font-medium">Skills (comma separated)</label>
                                <input
                                    type="text"
                                    name="skills"
                                    value={formData.skills.join(", ")}
                                    onChange={(e) =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            skills: e.target.value.split(",").map((s) => s.trim()),
                                        }))
                                    }
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                                />
                            </div>


                            <div>
                                <label className="block text-gray-600 mb-1 font-medium">Resume Link</label>
                                <input
                                    type="url"
                                    name="resumeLink"
                                    value={formData.resumeLink}
                                    onChange={handleChange}
                                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                                />
                            </div>


                            <div className="flex justify-end gap-4 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="px-5 py-2 rounded-lg bg-gray-300 hover:bg-gray-400 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    onClick={() => toast.success("Updated Successfully")}
                                    className="px-5 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
                                >
                                    Save
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

        </div >
    );
};

export default Profile;

