import React, { useContext } from 'react'
import Login from './pages/Login'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css';
import {AdminContext} from './context/AdminContext'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Admin/Dashboard'
import AllAppointments from './pages/Admin/AllAppointments'
import AddDoctor from './pages/Admin/AddDoctor'
import DoctorList from './pages/Admin/DoctorList'
import DoctorDashboard from './pages/Doctors/DoctorDashboard'
import { DoctorContext } from './context/DoctorContext';
import DoctorProfile from './pages/Doctors/DoctorProfile';
import DoctorAppointments from './pages/Doctors/DoctorAppointments';

const App = () => {

  const {aToken} = useContext(AdminContext)
  const {dToken} = useContext(DoctorContext)


  return aToken || dToken ? (
    <div className='bg-[#F8F9FD]'>
      <ToastContainer />
      <Navbar />
      <div className='flex items-start'>
        <Sidebar />
        <Routes>
          {/* Admin Routes */}
          <Route path='/' element={<> </>}></Route>
          <Route path='/admin-dashboard' element={<Dashboard />}></Route>
          <Route path='/all-appointments' element={<AllAppointments />}></Route>
          <Route path='/add-doctor' element={<AddDoctor />}></Route>
          <Route path='/doctor-list' element={<DoctorList />}></Route>

          {/* Doctors Routes */}
          <Route path='/doctor-dashboard' element={<DoctorDashboard />}></Route>
          <Route path='/doctor-profile' element={< DoctorProfile/>}></Route>
          <Route path='/doctor-appointments' element={<DoctorAppointments />}></Route>
        </Routes>
      </div>
    </div>
  ): (
    <>
      <Login />
      <ToastContainer />
    </>
  )
}

export default App
