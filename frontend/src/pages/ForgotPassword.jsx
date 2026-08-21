import React, { useState } from 'react'
import axios from 'axios'
import { toast } from 'react-toastify'
import { useNavigate } from 'react-router-dom'

const ForgotPassword = () => {
  const backendUrl = import.meta.env.VITE_BACKEND_URL
  const navigate = useNavigate()

  const [accountId, setAccountId] = useState('')
  const [email, setEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    try {
      setLoading(true)
      const { data } = await axios.post(`${backendUrl}/api/auth/forgot-password`, {
        accountType: 'user',
        accountId,
        email,
        newPassword,
      })

      if (data.success) {
        toast.success(data.message)
        navigate('/login')
      } else {
        toast.error(data.message)
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} className='min-h-[80vh] flex items-center'>
      <div className='flex flex-col gap-3 m-auto items-start p-8 min-w-[340px] sm:min-w-96 border rounded-xl text-zinc-600 text-sm shadow-lg'>
        <p className='text-2xl font-semibold'>Reset Password</p>
        <p className='text-gray-500'>Verify your User ID and registered email.</p>

        <div className='w-full'>
          <p>User ID</p>
          <input className='border border-zinc-300 rounded w-full p-2 mt-1' value={accountId} onChange={e => setAccountId(e.target.value)} placeholder='MongoDB User ID' required />
        </div>
        <div className='w-full'>
          <p>Email</p>
          <input className='border border-zinc-300 rounded w-full p-2 mt-1' type='email' value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className='w-full'>
          <p>New Password</p>
          <input className='border border-zinc-300 rounded w-full p-2 mt-1' type='password' minLength='8' value={newPassword} onChange={e => setNewPassword(e.target.value)} required />
        </div>
        <div className='w-full'>
          <p>Confirm Password</p>
          <input className='border border-zinc-300 rounded w-full p-2 mt-1' type='password' minLength='8' value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
        </div>

        <button disabled={loading} className='bg-primary text-white w-full py-2 rounded-md text-base disabled:opacity-60'>
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
        <button type='button' onClick={() => navigate('/login')} className='text-primary underline w-full'>Back to Login</button>
      </div>
    </form>
  )
}

export default ForgotPassword
