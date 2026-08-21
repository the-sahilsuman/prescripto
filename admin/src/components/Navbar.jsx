import React, { useContext } from 'react'
import axios from 'axios'
import { assets } from '../assets/assets.js'
import { AdminContext } from '../context/AdminContext'
import { useNavigate } from 'react-router-dom'
import {DoctorContext} from '../context/DoctorContext'

const Navbar = () => {

  const {aToken, aRefreshToken, setAToken, setARefreshToken, backendUrl} = useContext(AdminContext)
  const {dToken, dRefreshToken, setDToken, setDRefreshToken, backendUrl: doctorBackendUrl} = useContext(DoctorContext)

  const navigate= useNavigate()

  const logout = async ()=>{
    navigate('/')

    const currentRefreshToken = aRefreshToken || dRefreshToken
    const apiUrl = backendUrl || doctorBackendUrl

    // Revoke the refresh token on the server BEFORE removing it locally.
    if (currentRefreshToken && apiUrl) {
      try {
        await axios.post(`${apiUrl}/api/auth/logout`, {
          refreshToken: currentRefreshToken,
        })
      } catch (error) {
        console.error('Logout token revocation failed:', error)
      }
    }

    // Always clear the browser session.
    if (aToken) {
      setAToken('')
      setARefreshToken('')
      localStorage.removeItem('aToken')
      localStorage.removeItem('aRefreshToken')
    }

    if (dToken) {
      setDToken('')
      setDRefreshToken('')
      localStorage.removeItem('dToken')
      localStorage.removeItem('dRefreshToken')
    }
  }

  return (
    <div className='flex justify-between items-center px-4 sm:px-10 py-3 border-b bg-white'>
      <div className='flex items-center gap-2 text-xs'>
        <img className='w-36 sm:w-40 cursor-pointer' src={assets.admin_logo} alt="" />
        <p className='border px-2.5 py-0.5 rounded-full border-gray-500 text-gray-600'>{aToken? 'Admin': 'Doctor'}</p>
      </div>
      <button onClick={logout} className='bg-primary text-white text-sm px-10 py-2 cursor-pointer rounded-full'>Logout</button>
    </div>
  )
}

export default Navbar
