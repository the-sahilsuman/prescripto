import { useEffect } from 'react'
import axios from 'axios'

/**
 * Refresh only when the backend says the access token is unauthorized/expired.
 * No timer is used. The original request is retried once with the new token.
 */
export function useTokenRefresh({
  refreshToken,
  backendUrl,
  token,
  tokenKey,
  refreshTokenKey,
  setToken,
  setRefreshToken,
}) {
  useEffect(() => {
    const interceptorId = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (!originalRequest || error.response?.status !== 401) {
          return Promise.reject(error)
        }

        // Only handle requests made with this context's current access token.
        const authHeader = originalRequest.headers?.Authorization || originalRequest.headers?.authorization
        const currentToken = token || localStorage.getItem(tokenKey)
        if (!currentToken || authHeader !== `Bearer ${currentToken}`) {
          return Promise.reject(error)
        }

        // Never intercept the refresh/logout endpoints themselves.
        if (originalRequest.url?.includes('/api/auth/refresh') || originalRequest.url?.includes('/api/auth/logout')) {
          return Promise.reject(error)
        }

        if (originalRequest._retry) {
          return Promise.reject(error)
        }

        originalRequest._retry = true

        const currentRefresh = refreshToken || localStorage.getItem(refreshTokenKey)
        if (!currentRefresh) {
          return Promise.reject(error)
        }

        try {
          const { data } = await axios.post(`${backendUrl}/api/auth/refresh`, {
            refreshToken: currentRefresh,
          })

          if (!data.success) {
            throw new Error(data.message || 'Refresh failed')
          }

          localStorage.setItem(tokenKey, data.token)
          localStorage.setItem(refreshTokenKey, data.refreshToken)
          setToken(data.token)
          setRefreshToken(data.refreshToken)

          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${data.token}`

          return axios(originalRequest)
        } catch (refreshError) {
          localStorage.removeItem(tokenKey)
          localStorage.removeItem(refreshTokenKey)
          setToken(false)
          setRefreshToken(false)
          return Promise.reject(refreshError)
        }
      }
    )

    return () => axios.interceptors.response.eject(interceptorId)
  }, [backendUrl, token, refreshToken, tokenKey, refreshTokenKey, setToken, setRefreshToken])
}
