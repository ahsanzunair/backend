import React from 'react'
import { Route, Routes } from 'react-router-dom'
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Message from './Pages/Message'
import Notifications from './Pages/Notifications'
import NotificationDetail from './Pages/NotificationDetails'
import Navbar from './Components/Navbar'
import Profile from './Pages/Profile'

const App = () => {
  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="/abc" element={<Message />} />
        <Route path="/" element={<Notifications />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/notifications/:id" element={<NotificationDetail />} />

      </Routes>
      <ToastContainer position="top-right" autoClose={2000} />

    </div>
  )
}

export default App 