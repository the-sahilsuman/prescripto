import { createContext, useState } from "react"
import axios from 'axios'
import { toast } from 'react-toastify'
import { useTokenRefresh } from '../hooks/useTokenRefresh'

export const DoctorContext = createContext()

const DoctorContextProvider = (props) => {

  const backendUrl = import.meta.env.VITE_BACKEND_URL

  const [dToken, setDToken] = useState(localStorage.getItem('dToken') ?? '')
  const [dRefreshToken, setDRefreshToken] = useState(localStorage.getItem('dRefreshToken') ?? '')

  const [appointments, setAppointments] = useState([])
  const [dashData, setDashData] = useState(null)
  const [profileData, setProfileData] = useState(false)

  // ── Silent 5-minute token refresh ─────────────────────────────────────────
  useTokenRefresh({
    refreshToken:    dRefreshToken,
    backendUrl,
    tokenKey:        'dToken',
    refreshTokenKey: 'dRefreshToken',
    setToken:        setDToken,
    setRefreshToken: setDRefreshToken,
  })

  // ── Auth header helper ─────────────────────────────────────────────────────
  const authHeader = () => ({ Authorization: `Bearer ${dToken}` })

  // ── API calls ──────────────────────────────────────────────────────────────

  const getAppointments = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/doctor/appointments', { headers: authHeader() })
      if (data.success) { setAppointments(data.appointments) }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const completeAppointment = async (appointmentId) => {
    try {
      const { data } = await axios.post(backendUrl + '/api/doctor/complete-appointment', { appointmentId }, { headers: authHeader() })
      if (data.success) { toast.success(data.message); getAppointments() }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const cancelAppointment = async (appointmentId) => {
    try {
      const { data } = await axios.post(backendUrl + '/api/doctor/cancel-appointment', { appointmentId }, { headers: authHeader() })
      if (data.success) { toast.success(data.message); getAppointments() }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const getDashData = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/doctor/dashboard', { headers: authHeader() })
      if (data.success) { setDashData(data.dashData) }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const getProfileData = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/doctor/profile', { headers: authHeader() })
      if (data.success) { setProfileData(data.profileData) }
    } catch (error) { toast.error(error.message) }
  }

  const value = {
    dToken, setDToken,
    dRefreshToken, setDRefreshToken,
    backendUrl,
    appointments, setAppointments, getAppointments,
    completeAppointment,
    cancelAppointment,
    dashData, setDashData, getDashData,
    profileData, setProfileData, getProfileData,
  }

  return (
    <DoctorContext.Provider value={value}>
      {props.children}
    </DoctorContext.Provider>
  )
}

export default DoctorContextProvider
