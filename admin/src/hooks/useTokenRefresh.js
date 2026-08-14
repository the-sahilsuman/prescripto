import { useEffect, useRef } from 'react'
import axios from 'axios'

const REFRESH_INTERVAL_MS = 5 * 60 * 1000  // 5 minutes

/**
 * Silently refreshes the access token every 5 minutes.
 *
 * @param {object} params
 * @param {string}   params.refreshToken     - Current refresh token (from localStorage / state)
 * @param {string}   params.backendUrl        - Base API URL
 * @param {string}   params.tokenKey          - localStorage key for the access token  (e.g. 'aToken')
 * @param {string}   params.refreshTokenKey   - localStorage key for the refresh token (e.g. 'aRefreshToken')
 * @param {Function} params.setToken          - State setter for the access token
 * @param {Function} params.setRefreshToken   - State setter for the refresh token
 */
export function useTokenRefresh({
  refreshToken,
  backendUrl,
  tokenKey,
  refreshTokenKey,
  setToken,
  setRefreshToken,
}) {
  // Keep a ref so the interval always sees the latest value without re-registering
  const refreshTokenRef = useRef(refreshToken)
  useEffect(() => { refreshTokenRef.current = refreshToken }, [refreshToken])

  useEffect(() => {
    // Don't schedule if there's nothing to refresh
    if (!refreshTokenRef.current) return

    const id = setInterval(async () => {
      const currentRefresh = refreshTokenRef.current
      if (!currentRefresh) return

      try {
        const { data } = await axios.post(`${backendUrl}/api/auth/refresh`, {
          refreshToken: currentRefresh,
        })

        if (data.success) {
          // Persist new tokens
          localStorage.setItem(tokenKey, data.token)
          localStorage.setItem(refreshTokenKey, data.refreshToken)

          // Update React state so downstream axios calls use the new token
          setToken(data.token)
          setRefreshToken(data.refreshToken)
        } else {
          // Refresh token rejected — clear everything, user must log in again
          localStorage.removeItem(tokenKey)
          localStorage.removeItem(refreshTokenKey)
          setToken('')
          setRefreshToken('')
        }
      } catch {
        // Network error or 401 — let it ride; next interval will retry
      }
    }, REFRESH_INTERVAL_MS)

    return () => clearInterval(id)
  // Only re-register when the backend URL changes (effectively once)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [backendUrl])
}
