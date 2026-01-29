import { FaUserAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const Navbar = () => {
    const navigate = useNavigate();

    return (
        <div className="w-full bg-white shadow px-6 py-4 flex justify-end items-center">
            
            <div className="relative group">
               
                <FaUserAlt className="text-2xl text-gray-700 cursor-pointer hover:text-gray-900 transition-colors duration-200" />

                
                <div className="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="flex flex-col py-2">
                        <p
                            onClick={() => navigate("/profile")}
                            className="px-4 py-2 text-black font-bold text-lg  hover:bg-gray-100  rounded cursor-pointer transition-colors duration-200"
                        >
                            Profile
                        </p>

                        <p
                            onClick={() => toast.success("Logout Successfully") }
                            className="px-4 py-2 text-black font-bold text-lg hover:bg-gray-100  rounded cursor-pointer transition-colors duration-200"
                        >
                            Logout
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Navbar;
