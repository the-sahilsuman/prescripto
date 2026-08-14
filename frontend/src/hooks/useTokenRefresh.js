import { useEffect, useRef } from 'react'
import axios from 'axios'

const REFRESH_INTERVAL_MS = 5 * 60 * 1000  // 5 minutes

/**
 * Silently refreshes the access token every 5 minutes.
 *
 * @param {object} params
 * @param {string}   params.refreshToken     - Current refresh token
 * @param {string}   params.backendUrl        - Base API URL
 * @param {string}   params.tokenKey          - localStorage key for the access token  (e.g. 'token')
 * @param {string}   params.refreshTokenKey   - localStorage key for the refresh token (e.g. 'refreshToken')
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
  const refreshTokenRef = useRef(refreshToken)
  useEffect(() => { refreshTokenRef.current = refreshToken }, [refreshToken])

  useEffect(() => {
    if (!refreshTokenRef.current) return

    const id = setInterval(async () => {
      const currentRefresh = refreshTokenRef.current
      if (!currentRefresh) return

      try {
        const { data } = await axios.post(`${backendUrl}/api/auth/refresh`, {
          refreshToken: currentRefresh,
        })

        if (data.success) {
          localStorage.setItem(tokenKey, data.token)
          localStorage.setItem(refreshTokenKey, data.refreshToken)
          setToken(data.token)
          setRefreshToken(data.refreshToken)
        } else {
          localStorage.removeItem(tokenKey)
          localStorage.removeItem(refreshTokenKey)
          setToken(false)
          setRefreshToken(false)
        }
      } catch {
        // Network error — silently retry on next interval
      }
    }, REFRESH_INTERVAL_MS)

    return () => clearInterval(id)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [backendUrl])
}
