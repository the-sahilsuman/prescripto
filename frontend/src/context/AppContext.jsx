import { createContext, useEffect, useState } from "react"
import axios from 'axios'
import { toast } from "react-toastify"
import { useTokenRefresh } from '../hooks/useTokenRefresh'

export const AppContext = createContext()

const AppContextProvider = (props) => {

  const currencysymbol = '$'
  const backendUrl = import.meta.env.VITE_BACKEND_URL

  const [doctors, setDoctors] = useState([])
  const [token, setToken] = useState(() => localStorage.getItem('token') || false)
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('refreshToken') || false)
  const [userData, setUserData] = useState(false)

  // ── Silent 5-minute token refresh ─────────────────────────────────────────
  useTokenRefresh({
    refreshToken,
    backendUrl,
    tokenKey:        'token',
    refreshTokenKey: 'refreshToken',
    setToken,
    setRefreshToken,
  })

  // ── Auth header helper ─────────────────────────────────────────────────────
  const authHeader = () => ({ Authorization: `Bearer ${token}` })

  // ── API calls ──────────────────────────────────────────────────────────────

  const getDoctorData = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/doctor/list')
      if (data.success) { setDoctors(data.doctors) }
      else { toast.error(data.message) }
    } catch (error) { toast.error(error.message) }
  }

  const loadUserProfileData = async () => {
    try {
      const { data } = await axios.get(backendUrl + '/api/user/get-profile', { headers: authHeader() })
      if (data.success) { setUserData(data.userData) }
      else { toast.error(data.message) }
    } catch (error) {
      // 401 = token expired or invalid — clear it silently, user just needs to log in
      if (error.response?.status === 401) {
        setToken(false)
        setRefreshToken(false)
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
      } else {
        toast.error(error.message)
      }
    }
  }

  const value = {
    doctors, getDoctorData,
    currencysymbol,
    token, setToken,
    refreshToken, setRefreshToken,
    backendUrl,
    userData, setUserData,
    loadUserProfileData,
  }

  useEffect(() => { getDoctorData() }, [])

  useEffect(() => {
    if (token) { loadUserProfileData() }
    else { setUserData(false) }
  }, [token])

  return (
    <AppContext.Provider value={value}>
      {props.children}
    </AppContext.Provider>
  )
}

export default AppContextProvider
