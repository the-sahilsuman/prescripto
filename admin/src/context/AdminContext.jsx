import { createContext, useState } from "react"
import axios from 'axios'
import { toast } from 'react-toastify'
import { useTokenRefresh } from '../hooks/useTokenRefresh'

export const AdminContext = createContext()

const AdminContextProvider = (props) => {

  const backendUrl = import.meta.env.VITE_BACKEND_URL

  const [aToken, setAToken] = useState(localStorage.getItem('aToken') ?? '')
  const [aRefreshToken, setARefreshToken] = useState(localStorage.getItem('aRefreshToken') ?? '')

  const [doctors, setDoctors] = useState([])
  const [appointments, setAppointments] = useState([])
  const [dashData, setDashData] = useState(false)

  // ── Silent 5-minute token refresh ─────────────────────────────────────────
  useTokenRefresh({
    token:           aToken,
    refreshToken:    aRefreshToken,
    backendUrl,
    tokenKey:        'aToken',
    refreshTokenKey: 'aRefreshToken',
    setToken:        setAToken,
    setRefreshToken: setARefreshToken,
  })

  // ── Auth header helper ─────────────────────────────────────────────────────
  const authHeader = () => ({ Authorization: `Bearer ${aToken}` })

  // ── API calls ──────────────────────────────────────────────────────────────

  const getAllDoctors = async () => {
    try {
      const { data } = await axios.post(backendUrl + '/api/admin/all-doctors', {}, { headers: authHeader() })
      if (data.success) { setDoctors(data.doctors) }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const changeAvailablity = async (docId) => {
    try {
      const { data } = await axios.post(backendUrl + '/api/admin/change-availability', { docId }, { headers: authHeader() })
      if (data.success) { toast.success(data.message); getAllDoctors() }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const getAllAppointments = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/admin/appointments', { headers: authHeader() })
      if (data.success) { setAppointments(data.appointments) }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const cancelAppointment = async (appointmentId) => {
    try {
      const { data } = await axios.post(backendUrl + '/api/admin/cancel-appointment', { appointmentId }, { headers: authHeader() })
      if (data.success) { toast.success(data.message); getAllAppointments() }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const getDashData = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/admin/dashboard', { headers: authHeader() })
      if (data.success) { setDashData(data.dashData) }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const value = {
    aToken, setAToken,
    aRefreshToken, setARefreshToken,
    backendUrl,
    doctors,
    getAllDoctors, changeAvailablity,
    appointments, setAppointments, getAllAppointments,
    cancelAppointment,
    dashData, getDashData,
  }

  return (
    <AdminContext.Provider value={value}>
      {props.children}
    </AdminContext.Provider>
  )
}

export default AdminContextProvider
